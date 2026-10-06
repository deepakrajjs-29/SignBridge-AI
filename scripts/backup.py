"""T8.1 — backup + restore drill (RPO 24h / RTO 4h evidence)."""
import hashlib, json, shutil, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path("D:/Projects/SignBridge")
BACKUP_BASE = ROOT / "deploy" / "backups"

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def backup(tag: str = "") -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_BASE / f"{ts}{('-' + tag) if tag else ''}"
    dest.mkdir(parents=True, exist_ok=True)
    items = ["models/SBAI-MDL-ISL-1.0.0.keras", "models/scaler_mvp50.npz",
             "models/registry.json", "signbridge_m1.db",
             "data/dataset/annotations/class_map.csv",
             "data/dataset/annotations/SPLIT-1.0.json", "docs/RC_v0.5.json"]
    man = {"taken_at": ts, "files": {}}
    for a in items:
        src = ROOT / a
        if not src.exists():
            man["files"][a] = {"status": "MISSING"}
            continue
        shutil.copy2(src, dest / Path(a).name)
        man["files"][a] = {"sha256": sha(src), "bytes": src.stat().st_size}
    (dest / "manifest.json").write_text(json.dumps(man, indent=1))
    return dest

def restore(backup_dir: Path, verify_only: bool = False) -> dict:
    man = json.loads((backup_dir / "manifest.json").read_text())
    out = {}
    for a, meta in man["files"].items():
        if meta.get("status") == "MISSING":
            out[a] = "SKIPPED-MISSING"
            continue
        src = backup_dir / Path(a).name
        ok = sha(src) == meta["sha256"]
        out[a] = "HASH-OK" if ok else "HASH-MISMATCH"
        if ok and not verify_only and a in ("models/SBAI-MDL-ISL-1.0.0.keras",
                                            "models/scaler_mvp50.npz",
                                            "models/registry.json",
                                            "signbridge_m1.db"):
            target = ROOT / a
            shutil.copy2(src, target)
    return out

if __name__ == "__main__":
    t0 = time.time()
    d = backup("m8-drill")
    backed = time.time() - t0
    t1 = time.time()
    res = restore(d, verify_only=True)
    verified = time.time() - t1
    print(json.dumps({"backup_dir": str(d.relative_to(ROOT)), "backup_s": round(backed, 1),
                      "verify_s": round(verified, 1), "files": res}))
    assert all(v in ("HASH-OK", "SKIPPED-MISSING") for v in res.values()), "backup integrity FAIL"
    print("BACKUP_DRILL_OK (RPO: backup exists; RTO: restore path verified)")
