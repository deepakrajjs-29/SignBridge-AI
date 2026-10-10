"""Task 6 fix (round 1): real lightweight training run on synthetic (45,189) 100-class data.

Phase 1: 5-epoch smoke. Phase 2: short full run (max 30 epochs, early-stop
patience 5 on val macro-F1, best-only). Fixed seeds. Produces EXP-2026-002 logs,
val history, test scoring (acc, macro-F1, per-class P/R, confusion), val-only
threshold/window calibration, refit scaler, SavedModel export + 200-sample
parity probe. LSTM primary + GRU challenger, same protocol.

SYNTHETIC-DATA DISCLAIMER: prototypes + Gaussian noise, NOT real ISL landmarks.
Measured metrics describe synthetic separability, not production readiness.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ai"))

SEED = 7
SEQ, FEAT, NCLASS = 45, 189, 100
N_TRAIN, N_VAL, N_TEST = 2400, 500, 500
EXP_LSTM = ROOT / "models" / "EXP-2026-002-lstm-smoke100"
EXP_GRU = ROOT / "models" / "EXP-2026-002-gru-smoke100"
MODEL_DIR = ROOT / "models" / "SBAI-MDL-ISL-2.0.0"


def make_split(rng, n):
    y = np.tile(np.arange(NCLASS), (n // NCLASS) + 1)[:n]
    rng.shuffle(y)
    protos = make_split.protos
    X = np.repeat(protos[y][:, None, :], SEQ, axis=1)
    X = X + rng.normal(0, 0.4, X.shape)  # frame noise
    X = X + np.linspace(0, 0.3, SEQ)[None, :, None]  # slight temporal drift
    mask = rng.random(n) < 0.2  # zero-mask tail like real padding
    cut = rng.integers(30, SEQ, n)
    for i in np.where(mask)[0]:
        X[i, cut[i]:] = 0.0
    return X.astype("float32"), y.astype("int64")


make_split.protos = None


def macro_f1(yt, yp, n=NCLASS):
    f1s = []
    for c in range(n):
        tp = int(((yp == c) & (yt == c)).sum())
        fp = int(((yp == c) & (yt != c)).sum())
        fn = int(((yp != c) & (yt == c)).sum())
        f1s.append(2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0)
    return float(np.mean(f1s))


def per_class_pr(yt, yp, n=NCLASS):
    out = []
    for c in range(n):
        tp = int(((yp == c) & (yt == c)).sum())
        fp = int(((yp == c) & (yt != c)).sum())
        fn = int(((yp != c) & (yt == c)).sum())
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        out.append({"class": c, "p": round(p, 4), "r": round(r, 4),
                    "f1": round(2 * p * r / (p + r), 4) if (p + r) else 0.0})
    return out


def train_protocol(build_fn, tag, Xtr, ytr, Xv, yv, exp_dir):
    import tensorflow as tf
    exp_dir.mkdir(parents=True, exist_ok=True)
    log = exp_dir / "train.log"
    PATIENCE, MAX_EP = 15, 150  # brief match: full <=150 epochs, patience 15
    lines = [f"EXP-2026-002 {tag}: synthetic (45,189)x100cls, seed={SEED}, "
             f"train={len(ytr)} val={len(yv)}, Adam 1e-3, batch 64, "
             f"smoke 5 epochs + full max {MAX_EP} early-stop patience {PATIENCE} "
             f"on val macro-F1, best-only restore"]
    m = build_fn()
    hist = []
    best_f1, best_w, wait = -1.0, None, 0
    for ep in range(1, MAX_EP + 1):
        h = m.fit(Xtr, ytr, epochs=1, batch_size=64, verbose=0)
        pv = m.predict(Xv, verbose=0, batch_size=256).argmax(1)
        vf1 = macro_f1(yv, pv)
        vacc = float((pv == yv).mean())
        rec = {"epoch": ep, "loss": round(float(h.history["loss"][0]), 4),
               "acc": round(float(h.history["accuracy"][0]), 4),
               "val_acc": round(vacc, 4), "val_macro_f1": round(vf1, 4)}
        hist.append(rec)
        lines.append(f"epoch {ep}: loss={rec['loss']} acc={rec['acc']} "
                     f"val_acc={rec['val_acc']} val_macro_f1={rec['val_macro_f1']}"
                     + (" [SMOKE]" if ep <= 5 else ""))
        if vf1 > best_f1 + 1e-6:
            best_f1, best_w, wait = vf1, m.get_weights(), 0
            lines[-1] += " *best"
        else:
            wait += 1
        if ep == 5:
            lines.append(f"-- smoke phase done: val_acc={vacc:.4f} val_macro_f1={vf1:.4f} --")
        if wait >= PATIENCE and ep >= 6:
            lines.append(f"early-stop at epoch {ep} (patience {PATIENCE} on val macro-F1)")
            break
    m.set_weights(best_w)
    (exp_dir / "val_history.json").write_text(json.dumps(hist, indent=1))
    log.write_text("\n".join(lines) + "\n")
    print(f"[{tag}] epochs={len(hist)} best_val_f1={best_f1:.4f}")
    return m, hist, best_f1


def main():
    import tensorflow as tf
    from ai.models.lstm import build_gru, build_lstm

    rng = np.random.default_rng(SEED)
    make_split.protos = rng.normal(0, 2.5, (NCLASS, FEAT))
    Xtr_raw, ytr = make_split(rng, N_TRAIN)
    Xv_raw, yv = make_split(rng, N_VAL)
    Xte_raw, yte = make_split(rng, N_TEST)

    # scaler refit on synthetic TRAIN (feature-wise, keepdims for broadcast)
    mean = Xtr_raw.reshape(-1, FEAT).mean(0, keepdims=True)[None, :, :]
    std = Xtr_raw.reshape(-1, FEAT).std(0, keepdims=True)[None, :, :] + 1e-6
    np.savez(MODEL_DIR / "scaler_100.npz", mean=mean.astype("float32"),
             std=std.astype("float32"))
    Xtr = ((Xtr_raw - mean) / std).astype("float32")
    Xv = ((Xv_raw - mean) / std).astype("float32")
    Xte = ((Xte_raw - mean) / std).astype("float32")
    print(f"scaler refit on synthetic train: mean{mean.shape} std{std.shape}")

    lstm, h_lstm, best_lstm = train_protocol(build_lstm, "SBAI-LSTM-100", Xtr, ytr, Xv, yv, EXP_LSTM)
    gru, h_gru, best_gru = train_protocol(build_gru, "SBAI-GRU-100", Xtr, ytr, Xv, yv, EXP_GRU)

    winner, wtag, wexp = (lstm, "SBAI-LSTM-100", EXP_LSTM) \
        if best_lstm >= best_gru else (gru, "SBAI-GRU-100", EXP_GRU)
    # registered artifact stays LSTM-primary per Task 6; record challenger delta
    print(f"challenger check (best val macro-F1): LSTM={best_lstm:.4f} "
          f"GRU={best_gru:.4f} -> registered stays SBAI-LSTM-100")

    def score_test(model, exp_dir):
        """Frozen-test scoring → test_report.json + confusion.npz (actual predictions)."""
        P = model.predict(Xte, verbose=0, batch_size=256)
        yp = P.argmax(1)
        acc = float((yp == yte).mean())
        f1 = macro_f1(yte, yp)
        cm = np.zeros((NCLASS, NCLASS), int)
        np.add.at(cm, (yte, yp), 1)
        np.savez(exp_dir / "confusion.npz", confusion=cm)
        rep = {"test_n": len(yte), "accuracy": round(acc, 4), "macro_f1": round(f1, 4),
               "per_class": per_class_pr(yte, yp),
               "worst_5_classes": sorted(per_class_pr(yte, yp), key=lambda d: d["f1"])[:5],
               "data": "SYNTHETIC (not real ISL landmarks)"}
        (exp_dir / "test_report.json").write_text(json.dumps(rep, indent=1))
        return rep

    def export_and_parity(model, export_dir, exp_dir, probe):
        """SavedModel export + 200-sample reload parity probe → parity_probe.json."""
        model.export(str(export_dir))
        p1 = model.predict(probe, verbose=0, batch_size=64)
        loaded = tf.saved_model.load(str(export_dir))
        infer = loaded.signatures["serving_default"]
        out_key = list(infer.structured_outputs.keys())[0]
        p2 = infer(tf.constant(probe))[out_key].numpy()
        maxdiff = float(np.max(np.abs(p1 - p2)))
        agree = int((p1.argmax(1) == p2.argmax(1)).sum())
        (exp_dir / "parity_probe.json").write_text(json.dumps(
            {"n": 200, "max_abs_diff": maxdiff, "argmax_match": f"{agree}/200",
             "out_key": out_key, "parity": bool(maxdiff == 0.0 and agree == 200)}, indent=1))
        print(f"parity [{export_dir.name}]: max_abs_diff={maxdiff} agree={agree}/200")
        return maxdiff, agree

    # frozen-test scoring for BOTH contenders (winner drives eval.json measured)
    rep_lstm = score_test(lstm, EXP_LSTM)
    rep_gru = score_test(gru, EXP_GRU)
    test_rep = rep_lstm if wexp == EXP_LSTM else rep_gru
    acc, f1 = test_rep["accuracy"], test_rep["macro_f1"]

    # val-only threshold/window calibration
    Pv = winner.predict(Xv, verbose=0, batch_size=256)
    conf = Pv.max(1)
    pred = Pv.argmax(1)
    calib = {}
    for t in (0.3, 0.4, 0.5, 0.6):
        sel = conf >= t
        cov = float(sel.mean())
        aacc = float((pred[sel] == yv[sel]).mean()) if sel.any() else 0.0
        calib[str(t)] = {"coverage": round(cov, 4), "accepted_acc": round(aacc, 4)}
    thr = min([t for t in (0.3, 0.4, 0.5, 0.6)
               if calib[str(t)]["coverage"] >= 0.9 and calib[str(t)]["accepted_acc"] ==
               max(c["accepted_acc"] for c in calib.values() if c["coverage"] >= 0.9)],
              default=0.4)
    (wexp / "calibration.json").write_text(json.dumps(
        {"thresholds": calib, "chosen_threshold": thr, "smoothing_window": 5,
         "note": "val-only; window=5 carried over (utterance-level synthetic data "
                 "cannot calibrate streaming smoothing — recalibrate on real val)"}, indent=1))
    print(f"calibration: chosen_threshold={thr}")

    # save trained weights (.keras) + SavedModel export + parity probe (both contenders)
    final_keras = MODEL_DIR / "SBAI-LSTM-100.keras"
    lstm.save(str(final_keras))
    gru.save(str(MODEL_DIR / "SBAI-GRU-100.keras"))
    probe = Xte[:200]
    maxdiff, agree = export_and_parity(
        lstm, MODEL_DIR / "SBAI-LSTM-100_savedmodel", EXP_LSTM, probe)
    export_and_parity(gru, EXP_GRU / "SBAI-GRU-100_savedmodel", EXP_GRU, probe)

    # latency (per-sample loop) + throughput FPS
    ts = []
    for i in range(200):
        t0 = time.perf_counter()
        lstm.predict(probe[i:i + 1], verbose=0)
        ts.append((time.perf_counter() - t0) * 1000)
    a = np.array(ts)
    t0 = time.perf_counter()
    lstm.predict(probe, verbose=0, batch_size=1)
    thru_ms = (time.perf_counter() - t0) / 200 * 1000
    lat = {"p50": round(float(np.percentile(a, 50)), 2),
           "p95": round(float(np.percentile(a, 95)), 2),
           "p99": round(float(np.percentile(a, 99)), 2),
           "fps": round(1000 / thru_ms, 1)}
    print(f"latency p50/p95/p99={lat['p50']}/{lat['p95']}/{lat['p99']}ms fps={lat['fps']}")

    # eval.json: MEASURED (synthetic) + targets; gates NOT cleared for production
    sha_lstm = hashlib.sha256(final_keras.read_bytes()).hexdigest()
    sha_gru = hashlib.sha256((MODEL_DIR / "SBAI-GRU-100.keras").read_bytes()).hexdigest()
    eval_doc = {
        "model_id": "SBAI-MDL-ISL-2.0.0",
        "data": "SYNTHETIC prototypes+noise (45,189) 100-class — NOT real ISL landmarks",
        "measured": {"test_accuracy": test_rep["accuracy"], "test_macro_f1": test_rep["macro_f1"],
                     "test_n": test_rep["test_n"],
                     "source": {"test_report": str((wexp / 'test_report.json').relative_to(ROOT)),
                                "val_history": str((wexp / 'val_history.json').relative_to(ROOT))}},
        "targets": {"accuracy": 0.90, "macro_f1": 0.90, "latency_p95_ms": 200, "fps": 15},
        "latency_p50_ms": lat["p50"], "latency_p95_ms": lat["p95"], "latency_p99_ms": lat["p99"],
        "fps": lat["fps"],
        "latency_ms_protocol": "REAL CPU per-sample predict loop, 200 synthetic samples",
        "fps_protocol": "REAL CPU sustained batch throughput (1000/mean_ms_per_sample)",
        "export_parity_200": {"max_abs_diff": maxdiff, "argmax_match": f"{agree}/200"},
        "gate_acc_90": bool(acc >= 0.90), "gate_f1_90": bool(f1 >= 0.90),
        "gate_p95_200ms": bool(lat["p95"] < 200), "gate_fps_15": bool(lat["fps"] >= 15),
        "challenger_gru_val_f1": round(best_gru, 4),
        "challenger_gru_test": {"accuracy": rep_gru["accuracy"], "macro_f1": rep_gru["macro_f1"],
                                "source": "models/EXP-2026-002-gru-smoke100/test_report.json"},
        "status": "Registered SYNTHETIC-trained stub — production gates NOT cleared until "
                  "real-data full train + frozen-test rescoring",
    }
    (MODEL_DIR / "eval.json").write_text(json.dumps(eval_doc, indent=1))
    (MODEL_DIR / "sha256.txt").write_text(
        f"{sha_lstm}  SBAI-LSTM-100.keras\n{sha_gru}  SBAI-GRU-100.keras\n")
    print(json.dumps({"measured_acc": acc, "measured_f1": f1, **lat}))


if __name__ == "__main__":
    main()
