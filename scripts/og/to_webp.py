#!/usr/bin/env python3
"""Convert the PNGs from make-og.js to WebP (quality 82) and delete the PNGs.
Needs Pillow: pip install pillow"""
import glob
import os

from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "images", "og")
for png in glob.glob(os.path.join(OUT, "*.png")):
    Image.open(png).convert("RGB").save(png[:-4] + ".webp", "WEBP", quality=82, method=6)
    os.remove(png)
pj = os.path.join(OUT, "pages.json")
if os.path.exists(pj):
    os.remove(pj)
print(len(glob.glob(os.path.join(OUT, "*.webp"))), "WebP share images")
