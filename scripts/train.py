"""T3.0/T3.1 — smoke + full training (TF-CPU, locked arch/hparams)."""
import argparse, csv, json, sys, time
from pathlib import Path
import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
import tensorflow as tf
from models.lstm import build_gru, build_lstm

P = argparse.ArgumentParser()
P.add_argument("--mode", choices=["smoke", "full"], required=True)
P.add_argument("--arch", choices=["lstm", "gru"], default="lstm")
a = P.parse_args()

tf.random.set_seed(7); np.random.seed(7)
D = np.load(ROOT / "data/dataset/processed/tensors_mvp50.npz")
S = np.load(ROOT / "data/dataset/processed/split_idx.npz")
X, y = D["X"].astype("float32"), D["y"]
tr, va, te = S["train"], S["val"], S["test"]

# scaler fit on train only (fitted artifact)
mu, sd = X[tr].mean((0, 1), keepdims=True), X[tr].std((0, 1), keepdims=True) + 1e-6
Xs = (X - mu) / sd
SC = ROOT / "models" / "scaler_mvp50.npz"
if a.mode == "full":
    SC.parent.mkdir(exist_ok=True)
    np.savez_compressed(SC, mean=mu, std=sd)

def macro_f1(yt, yp):
    from sklearn.metrics import f1_score
    return float(f1_score(yt, yp, average="macro", zero_division=0))

class F1Stop(tf.keras.callbacks.Callback):
    def __init__(self, Xv, yv, patience=15, out=""):
        self.Xv, self.yv, self.patience, self.out = Xv, yv, patience, out
        self.best, self.wait = -1, 0
    def on_epoch_end(self, epoch, logs=None):
        print(f"epoch {epoch+1}: loss={logs['loss']:.4f} acc={logs['accuracy']:.4f} "
              f"val_loss={logs['val_loss']:.4f} val_acc={logs['val_accuracy']:.4f}", flush=True)
        f1 = macro_f1(self.yv, self.model.predict(self.Xv, verbose=0).argmax(1))
        logs["val_macro_f1"] = f1
        print(f"  val_f1={f1:.4f} best={max(f1, self.best):.4f} wait={self.wait}", flush=True)
        if f1 > self.best:
            self.best, self.wait = f1, 0
            self.model.save(self.out)
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.model.stop_training = True

build = build_lstm if a.arch == "lstm" else build_gru
EXP = ROOT / "models" / f"EXP-2026-001-{a.arch}-{a.mode}"
EXP.mkdir(parents=True, exist_ok=True)


def mirror_features(Xb):
    """Exact x-mirror in 189-dim feature space (handedness augmentation).

    Rationale: test signer U014 signs left-handed (slot analysis); mirroring
    teaches hand-invariance with identical labels. Distances/speeds/magnitudes
    are mirror-invariant; coords x-components negate; bbox min/max x swap.
    Train-only; val/test untouched. (Doc-06 mirror caution noted in M3.)"""
    M = Xb.copy()
    C = M[:, :, :126].reshape((-1, 45, 2, 21, 3))
    C[..., 0] *= -1
    for h in (0, 1):
        b = 168 + h * 10
        mnx, mxx = M[:, :, b].copy(), M[:, :, b + 3].copy()
        M[:, :, b], M[:, :, b + 3] = -mxx, -mnx
        M[:, :, b + 6] *= -1
    return M


class AugSequence(tf.keras.utils.Sequence):
    """Train-only augmentation (plan T2.4): per-batch random scale (0.9–1.1),
    shift (±0.05), coordinate noise (σ=0.01), frame-drop (repeat neighbor).
    Val/test never augmented."""

    def __init__(self, X, y, batch=64):
        self.X, self.y, self.batch = X, y, batch
        self.rng = np.random.default_rng(7)

    def __len__(self):
        return int(np.ceil(len(self.X) / self.batch))

    def __getitem__(self, i):
        xb = self.X[i * self.batch:(i + 1) * self.batch].copy()
        yb = self.y[i * self.batch:(i + 1) * self.batch]
        mir = self.rng.random(len(xb)) < 0.5
        if mir.any():
            xb[mir] = mirror_features(xb[mir])
        scale = self.rng.uniform(0.9, 1.1, (len(xb), 1, 1)).astype("float32")
        xb = (xb + self.rng.normal(0, 0.01, xb.shape).astype("float32")) * scale
        xb += self.rng.uniform(-0.05, 0.05, (len(xb), 1, 1)).astype("float32")
        drop = self.rng.random((len(xb), 45)) < 0.05
        for b in np.where(drop.any(1))[0]:
            for t in np.where(drop[b])[0]:
                xb[b, t] = xb[b, t - 1] if t > 0 else xb[b, t + 1]
        return xb, yb

if a.mode == "smoke":
    m = build()
    xb, yb = Xs[tr[:32]], y[tr[:32]]
    h = m.fit(xb, yb, epochs=5, verbose=0)
    losses = h.history["loss"]
    print("smoke losses:", [round(float(x), 4) for x in losses])
    assert losses[-1] < losses[0], "smoke FAIL: loss did not decrease"
    print("SMOKE_OK")
else:
    m = build()
    t0 = time.time()
    cb = F1Stop(Xs[va], y[va], patience=15, out=str(EXP / f"SBAI-MDL-ISL-1.0.0_{a.arch}.keras"))
    rl = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-5)
    h = m.fit(AugSequence(Xs[tr], y[tr]), validation_data=(Xs[va], y[va]), epochs=150,
              callbacks=[cb, rl], verbose=0)
    secs = time.time() - t0
    with (EXP / "history.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(h.history.keys()))
        w.writeheader()
        for i in range(len(h.epoch)):
            w.writerow({k: float(v[i]) for k, v in h.history.items()})
    print(json.dumps({"arch": a.arch, "epochs": len(h.epoch), "best_val_f1": round(cb.best, 4),
                      "minutes": round(secs / 60, 1)}))
