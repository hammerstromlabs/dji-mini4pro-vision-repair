"""Characterise recorded camera frames: brightness, spatial correlation, frame-to-frame change."""
import glob
import os
import sys
import numpy as np
from PIL import Image

root = sys.argv[1]
for cam in ("0", "1"):
    files = sorted(glob.glob(os.path.join(root, cam, "*.png")), key=lambda p: int(os.path.basename(p)[:-4]))
    frames = [np.asarray(Image.open(f), dtype=np.float32) for f in files]
    print(f"\n=== camera {cam}: {len(frames)} frames, shape {frames[0].shape}")
    for i in (0, len(frames) // 2, len(frames) - 1):
        a = frames[i]
        # Correlation between horizontally / vertically adjacent pixels: ~0 for white noise, ~1 for real images.
        h = np.corrcoef(a[:, :-1].ravel(), a[:, 1:].ravel())[0, 1]
        v = np.corrcoef(a[:-1, :].ravel(), a[1:, :].ravel())[0, 1]
        hist = np.bincount(a.astype(np.uint8).ravel(), minlength=256)
        print(f"  frame {i:2d}: mean {a.mean():6.1f} std {a.std():5.1f} min {a.min():3.0f} max {a.max():3.0f} "
              f"adjH {h:+.3f} adjV {v:+.3f} distinct {np.count_nonzero(hist)}")
    diffs = [np.abs(frames[i + 1] - frames[i]).mean() for i in range(len(frames) - 1)]
    print(f"  mean |frame[i+1]-frame[i]|: min {min(diffs):.2f} max {max(diffs):.2f}")
    # Row/column mean profiles reveal banding or lane-misalignment structure hidden in noise.
    a = np.mean(frames, axis=0)
    print(f"  time-averaged: std {a.std():.2f}, row-mean std {a.mean(axis=1).std():.2f}, col-mean std {a.mean(axis=0).std():.2f}")
    col = a.mean(axis=0)
    print("  col means (period check, first 16):", np.round(col[:16], 1).tolist())
