from __future__ import annotations
import argparse, pathlib, re
import cv2
import pytesseract
from loguru import logger

def extract_ids(path: str) -> list[str]:
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"Cannot read image {path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    text = pytesseract.image_to_string(gray, config="--oem 3 --psm 6")
    ids = set(re.findall(r"[A-Z0-9]{6,12}", text.replace("\n", " ")))
    return list(ids)

def compare(form_path: str, label_path: str) -> dict:
    form_ids = set(extract_ids(form_path))
    label_ids = set(extract_ids(label_path))
    overlap = form_ids & label_ids
    confidence = 0.0
    if overlap:
        confidence = 0.9
    elif any(x in y or y in x for x in form_ids for y in label_ids):
        confidence = 0.6
    else:
        confidence = 0.2
    return {"form_ids": sorted(form_ids), "label_ids": sorted(label_ids), "match": sorted(overlap), "confidence": confidence}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", required=True, help="Path to form image")
    ap.add_argument("--label", required=True, help="Path to sidecar label image")
    args = ap.parse_args()
    res = compare(args.form, args.label)
    logger.info(res)

if __name__ == "__main__":
    main()
