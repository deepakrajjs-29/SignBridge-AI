"""V3+ smoke + full training on REAL tensors (TF-CPU, locked arch/hparams).

Mirrors scripts/train.py exactly (Adam 1e-3, ReduceLROnPlateau, early-stop
patience 15 on val macro-F1, batch 64, <=150 epochs, train-only mirror +
scale/shift/noise/drop aug). Class count derives from class_map; --tag,
--exp and --model-id select the artifact family (defaults = 100-class v3).
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("D:/Projects/SignBridge")
sys.path.insert(0, str(ROOT / "ai"))
import tensorflow as tf
from models.lstm import build_gru, build_lstm

P = argparse.ArgumentParser()
P.add_argument("--mode", choices=["smoke", "full"], required=True)
P.add_argument("--arch", choices=["lstm", "gru"], default="lstm")
P.add_argument("--tag", default="100_real")
P.add_argument("--exp", default="EXP-2026-003")
P.add_argument("--model-id", default="SBAI-MDL-ISL-3.0.0")
P.add_argument("--time-jitter", action="store_true",
               help="train-only: circular time-roll r in [-4,4] before other augs (M13 Task 7)")
P.add_argument("--feat-dim", type=int, default=189,
               help="model input feature dim (189 = FV-1.0, 193 = FV-1.0+traj)")
P.add_argument("--scaler-file", default="",
               help="scaler npz basename under models/ (default: scaler_{split}_real.npz)")
a = P.parse_args()

NCLASS = len(list(csv.DictReader(
    (ROOT / "data/dataset/annotations/class_map.csv").open(encoding="utf-8"))))
SPLIT_TAG = a.tag.split("_")[0]

tf.random.set_seed(7)
np.random.seed(7)
D = np.load(ROOT / "data/dataset/processed" / f"tensors_{a.tag}.npz")
S = np.load(ROOT / "data/dataset/processed" / f"split_idx_{SPLIT_TAG}.npz")
X, y = D["X"].astype("float32"), D["y"]
tr, va, te = S["train"], S["val"], S["test"]
assert len(np.unique(y)) == NCLASS, f"expected {NCLASS} classes, got {len(np.unique(y))}"

# scaler fit on train only (fitted artifact)
mu, sd = X[tr].mean((0, 1), keepdims=True), X[tr].std((0, 1), keepdims=True) + 1e-6
Xs = (X - mu) / sd
SC = ROOT / "models" / (a.scaler_file or f"scaler_{SPLIT_TAG}_real.npz")
assert X.shape[-1] == a.feat_dim, f"tensor feat {X.shape[-1]} != --feat-dim {a.feat_dim}"
if a.mode == "full":
    SC.parent.mkdir(exist_ok=True)
    if SC.exists():
        # Deterministic given the same train split; never overwrite existing artifacts.
        print(f"scaler exists — not overwriting: {SC}", flush=True)
    else:
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


def mirror_features(Xb):
    """Exact x-mirror in 189-dim feature space (same as train.py).

    For 193-dim FV rows the appended global-wrist trajectory mirrors too:
    u (col 189) and du (col 191) are negated like the wrist-relative coords.
    """
    M = Xb.copy()
    C = M[:, :, :126].reshape((-1, 45, 2, 21, 3))
    C[..., 0] *= -1
    for h in (0, 1):
        b = 168 + h * 10
        mnx, mxx = M[:, :, b].copy(), M[:, :, b + 3].copy()
        M[:, :, b], M[:, :, b + 3] = -mxx, -mnx
        M[:, :, b + 6] *= -1
    if M.shape[-1] >= 193:
        M[:, :, 189] *= -1
        M[:, :, 191] *= -1
    return M


class AugSequence(tf.keras.utils.Sequence):
    """Train-only augmentation (same as train.py). Val/test never augmented:
    this class is only ever constructed with the train slice (Xs[tr], y[tr]);
    validation_data is the raw (Xs[va], y[va]) tuple and the test slice is
    never passed to fit()."""

    def __init__(self, X, y, batch=64, time_jitter=False):
        self.X, self.y, self.batch = X, y, batch
        self.time_jitter = time_jitter
        self.rng = np.random.default_rng(7)

    def __len__(self):
        return int(np.ceil(len(self.X) / self.batch))

    def __getitem__(self, i):
        xb = self.X[i * self.batch:(i + 1) * self.batch].copy()
        yb = self.y[i * self.batch:(i + 1) * self.batch]
        if self.time_jitter:
            # circular roll along the time axis of each (T, F) sample
            # (np.roll axis=0 per sample == batch axis 1), r in [-4, 4] uniform
            # (includes 0), applied BEFORE mirror/scale/shift/noise/drop
            rs = self.rng.integers(-4, 5, size=len(xb))
            xb = np.stack([np.roll(x, int(r), axis=0) for x, r in zip(xb, rs)]).astype("float32")
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


build = ((lambda: build_lstm(nclass=NCLASS, feat_dim=a.feat_dim)) if a.arch == "lstm"
         else (lambda: build_gru(nclass=NCLASS, feat_dim=a.feat_dim)))
EXP = ROOT / "models" / f"{a.exp}-{a.arch}-{a.mode}"
EXP.mkdir(parents=True, exist_ok=True)

if a.mode == "smoke":
    m = build()
    if a.time_jitter:
        # exercise the jittered AugSequence path (train slice only; same
        # AugSequence used in full mode)
        h = m.fit(AugSequence(Xs[tr[:32]], y[tr[:32]], time_jitter=True), epochs=5, verbose=0)
    else:
        xb, yb = Xs[tr[:32]], y[tr[:32]]
        h = m.fit(xb, yb, epochs=5, verbose=0)
    losses = h.history["loss"]
    print("smoke losses:", [round(float(x), 4) for x in losses], flush=True)
    assert losses[-1] < losses[0], "smoke FAIL: loss did not decrease"
    print("SMOKE_OK", flush=True)
else:
    m = build()
    t0 = time.time()
    OUT = EXP / f"{a.model_id}_{a.arch}.keras"
    assert not OUT.exists(), f"refusing to overwrite existing model: {OUT}"
    cb = F1Stop(Xs[va], y[va], patience=15, out=str(OUT))
    rl = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=5, min_lr=1e-5)
    # train slice only: val/test never augmented (AugSequence never sees va/te)
    h = m.fit(AugSequence(Xs[tr], y[tr], time_jitter=a.time_jitter),
              validation_data=(Xs[va], y[va]), epochs=150,
              callbacks=[cb, rl], verbose=0)
    secs = time.time() - t0
    with (EXP / "history.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(h.history.keys()))
        w.writeheader()
        for i in range(len(h.epoch)):
            w.writerow({k: float(v[i]) for k, v in h.history.items()})
    print(json.dumps({"arch": a.arch, "epochs": len(h.epoch), "best_val_f1": round(cb.best, 4),
                      "minutes": round(secs / 60, 1)}), flush=True)
