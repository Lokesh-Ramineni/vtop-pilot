import base64
import io
import json
import os
import logging
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_PATH=ROOT_DIR / "Weights"/"captcha_weights.npz"
LABELS_PATH=ROOT_DIR / "Weights"/"labels.json"
IMG_SIZE = 32
CAPTCHA_LEN = 6


try:
    _weights = dict(np.load(WEIGHTS_PATH))
    with open(LABELS_PATH) as f:
        CLASSES = json.load(f)
except FileNotFoundError:
    logger.error(f"Error: {WEIGHTS_PATH} or {LABELS_PATH} not found. Run export_weights.py first.")
    _weights = None
    CLASSES = None
except Exception as e:
    logger.error(f"Error loading captcha weights: {e}")
    _weights = None
    CLASSES = None


def _conv2d(x: np.ndarray, weight: np.ndarray, bias: np.ndarray, padding: int = 1) -> np.ndarray:
    Cin, H, W = x.shape
    Cout, _, kh, kw = weight.shape

    xp = np.pad(x, ((0, 0), (padding, padding), (padding, padding)))
    Hp, Wp = xp.shape[1], xp.shape[2]
    H_out, W_out = Hp - kh + 1, Wp - kw + 1

    shape = (Cin, kh, kw, H_out, W_out)
    strides = (xp.strides[0], xp.strides[1], xp.strides[2], xp.strides[1], xp.strides[2])
    patches = np.lib.stride_tricks.as_strided(xp, shape=shape, strides=strides)
    patches = patches.reshape(Cin * kh * kw, H_out * W_out)

    w_flat = weight.reshape(Cout, Cin * kh * kw)
    out = w_flat @ patches + bias[:, None]
    return out.reshape(Cout, H_out, W_out)


def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0)


def _maxpool2x2(x: np.ndarray) -> np.ndarray:
    C, H, W = x.shape
    H2, W2 = H // 2, W // 2
    x = x[:, :H2 * 2, :W2 * 2].reshape(C, H2, 2, W2, 2)
    return x.max(axis=(2, 4))


def _linear(x: np.ndarray, weight: np.ndarray, bias: np.ndarray) -> np.ndarray:
    return weight @ x + bias


def _forward(x: np.ndarray) -> np.ndarray:
    w = _weights
    h = _relu(_conv2d(x, w["conv1.weight"], w["conv1.bias"]))
    h = _relu(_conv2d(h, w["conv2.weight"], w["conv2.bias"]))
    h = _maxpool2x2(h)
    h = _relu(_conv2d(h, w["conv3.weight"], w["conv3.bias"]))
    h = _relu(_conv2d(h, w["conv4.weight"], w["conv4.bias"]))
    h = _maxpool2x2(h)
    h = h.flatten()
    h = _relu(_linear(h, w["fc1.weight"], w["fc1.bias"]))
    h = _linear(h, w["fc2.weight"], w["fc2.bias"])
    return h


def _otsu_threshold(gray: np.ndarray) -> int:
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    total = gray.size
    sum_all = np.dot(np.arange(256), hist)

    sum_b, w_b, max_var, threshold = 0.0, 0.0, 0.0, 0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_all - sum_b) / w_f
        var_between = w_b * w_f * (m_b - m_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold = t

    return threshold


def _redness_mask(img_rgb: np.ndarray) -> np.ndarray:
    r = img_rgb[:, :, 0].astype(np.int16)
    g = img_rgb[:, :, 1].astype(np.int16)
    b = img_rgb[:, :, 2].astype(np.int16)
    return np.clip(r - (g + b) / 2, 0, 255).astype(np.uint8)


def _split_wide_boxes(boxes, expected_count):
    boxes = sorted(boxes, key=lambda bb: bb[0])
    guard = 0
    while len(boxes) < expected_count and guard < 10:
        widths = [bb[2] for bb in boxes]
        idx = widths.index(max(widths))
        x, y, w, h = boxes[idx]
        half = w // 2
        boxes[idx:idx+1] = [(x, y, half, h), (x + half, y, w - half, h)]
        boxes = sorted(boxes, key=lambda bb: bb[0])
        guard += 1
    return boxes


def _segment_letters(img_rgb: np.ndarray, expected_count: int = CAPTCHA_LEN):
    redness = _redness_mask(img_rgb)
    padded = np.pad(redness, 8, mode="edge")

    t = _otsu_threshold(padded)
    mask = padded > t

    close_struct = np.ones((9, 3), dtype=bool)
    closed = ndimage.binary_closing(mask, structure=close_struct)
    open_struct = np.ones((2, 2), dtype=bool)
    closed = ndimage.binary_opening(closed, structure=open_struct)

    labeled, _ = ndimage.label(closed)
    objects = ndimage.find_objects(labeled)

    img_area = padded.shape[0] * padded.shape[1]
    min_area = img_area * 0.006

    boxes = []
    for sl in objects:
        if sl is None:
            continue
        y1, y2 = sl[0].start, sl[0].stop
        x1, x2 = sl[1].start, sl[1].stop
        area = (y2 - y1) * (x2 - x1)
        if area >= min_area:
            boxes.append((x1, y1, x2 - x1, y2 - y1))

    boxes = sorted(boxes, key=lambda bb: bb[0])

    if expected_count is not None:
        if len(boxes) < expected_count:
            boxes = _split_wide_boxes(boxes, expected_count)
        elif len(boxes) > expected_count:
            boxes = sorted(boxes, key=lambda bb: bb[2] * bb[3], reverse=True)[:expected_count]
            boxes = sorted(boxes, key=lambda bb: bb[0])

    closed_uint8 = (closed * 255).astype(np.uint8)

    crops = []
    for (x, y, w, h) in boxes:
        x1, y1 = max(0, x - 2), max(0, y - 2)
        x2, y2 = min(closed_uint8.shape[1], x + w + 2), min(closed_uint8.shape[0], y + h + 2)
        crops.append(closed_uint8[y1:y2, x1:x2])

    return crops


def _resize_and_pad(img: np.ndarray, size: int = IMG_SIZE) -> np.ndarray:
    h, w = img.shape
    scale = size / max(h, w)
    new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))

    resized = np.array(Image.fromarray(img).resize((new_w, new_h), Image.Resampling.LANCZOS))

    canvas = np.zeros((size, size), dtype=np.uint8)
    y_off, x_off = (size - new_h) // 2, (size - new_w) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized
    return canvas


def _str_to_img(src: str) -> np.ndarray:
    try:
        im_bytes = base64.b64decode(src)
        pil_img = Image.open(io.BytesIO(im_bytes)).convert("RGB")
        return np.array(pil_img)
    except Exception as e:
        logger.error(f"Error decoding base64 to image: {e}")
        raise ValueError(f"Failed to decode base64 to image: {e}") from e

def solve_captcha_ml(img_rgb: np.ndarray) -> str:
    if _weights is None:
        raise RuntimeError("Weights not loaded — run export_weights.py first.")

    crops = _segment_letters(img_rgb, expected_count=CAPTCHA_LEN)
    if len(crops) != CAPTCHA_LEN:
        raise ValueError(
            f"Segmentation produced {len(crops)} characters, expected {CAPTCHA_LEN}"
        )

    captcha = ""
    for crop in crops:
        resized = _resize_and_pad(crop).astype("float32") / 255.0
        x = resized[np.newaxis, :, :]
        logits = _forward(x)
        captcha += CLASSES[int(np.argmax(logits))]

    if len(captcha) != CAPTCHA_LEN:
        logger.error(f"Warning: Captcha solving resulted in unexpected output: {captcha}")
        raise ValueError(f"Captcha solving resulted in unexpected output: {captcha}")

    return captcha


def solve_captcha(captcha_base64: str) -> str:
    """
    Solves the given base64 encoded captcha image using the exported CNN weights.

    Args:
        captcha_base64 (str): Base64 encoded captcha image data (excluding prefix).

    Returns:
        str: The predicted captcha text.
    """
    try:
        img = _str_to_img(captcha_base64)
        return solve_captcha_ml(img)
    except Exception as e:
        logger.error(f"An unexpected error occurred during captcha solving: {e}")
        raise
