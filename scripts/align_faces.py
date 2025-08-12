"""
Align and square-crop headshots so faces are centered consistently.

Usage:
  python3 scripts/align_faces.py /path/to/img1.png /path/to/img2.png ...

Outputs files with suffix "_aligned.png" next to each input.
"""

from __future__ import annotations

import sys
import os
from typing import Tuple, Any, cast


def ensure_opencv_available() -> None:
    try:
        import cv2  # type: ignore  # noqa: F401
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "OpenCV (cv2) is required. Install with: pip install opencv-python-headless"
        ) from exc


def detect_primary_face_bounds(image_bgr) -> Tuple[int, int, int, int] | None:
    import cv2 as _cv2  # type: ignore
    cv2 = cast(Any, _cv2)

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    # Choose the largest face by area
    x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
    return int(x), int(y), int(w), int(h)


def crop_to_centered_square(image_bgr, center_x: int, center_y: int, side: int):
    import cv2 as _cv2  # type: ignore
    cv2 = cast(Any, _cv2)
    h, w = image_bgr.shape[:2]
    half = side // 2
    left = max(0, center_x - half)
    top = max(0, center_y - half)
    right = min(w, left + side)
    bottom = min(h, top + side)

    # Adjust if at edge
    left = max(0, right - side)
    top = max(0, bottom - side)

    cropped = image_bgr[top:bottom, left:right]
    # If crop is not square due to edges, pad with border to square
    ch, cw = cropped.shape[:2]
    if ch != cw:
        pad = abs(ch - cw)
        if ch < cw:
            top_pad = pad // 2
            bottom_pad = pad - top_pad
            cropped = cv2.copyMakeBorder(
                cropped, top_pad, bottom_pad, 0, 0, cv2.BORDER_REPLICATE
            )
        else:
            left_pad = pad // 2
            right_pad = pad - left_pad
            cropped = cv2.copyMakeBorder(
                cropped, 0, 0, left_pad, right_pad, cv2.BORDER_REPLICATE
            )
    return cropped


def align_image(path: str, output_size: int = 300) -> str:
    import cv2 as _cv2  # type: ignore
    cv2 = cast(Any, _cv2)

    image_bgr = cv2.imread(path)
    if image_bgr is None:
        raise FileNotFoundError(path)

    bounds = detect_primary_face_bounds(image_bgr)
    h, w = image_bgr.shape[:2]

    if bounds is None:
        # Fallback: center square crop
        center_x, center_y = w // 2, h // 2
        side = min(w, h)
    else:
        x, y, fw, fh = bounds
        # Center on face with padding factor
        center_x = x + fw // 2
        center_y = y + fh // 2
        side = int(max(fw, fh) * 2.0)
        side = min(side, min(w, h))

    cropped = crop_to_centered_square(image_bgr, center_x, center_y, side)
    resized = cv2.resize(cropped, (output_size, output_size), interpolation=cv2.INTER_LANCZOS4)

    root, _ = os.path.splitext(path)
    out_path = f"{root}_aligned.png"
    cv2.imwrite(out_path, resized)
    return out_path


def main(argv: list[str]) -> None:
    ensure_opencv_available()
    if len(argv) < 2:
        print("Usage: python3 scripts/align_faces.py <image1> <image2> ...")
        raise SystemExit(2)

    inputs = argv[1:]
    for p in inputs:
        out = align_image(p)
        print(out)


if __name__ == "__main__":
    main(sys.argv)


