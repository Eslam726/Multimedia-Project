import numpy as np
from PIL import Image


def apply_visible_watermark(img: Image.Image, wm: Image.Image, opacity: float = 0.55) -> Image.Image:
    base = img.convert("RGBA")
    mark = wm.convert("RGBA").resize(base.size, Image.LANCZOS)
    r, g, b, a = mark.split()
    a = a.point(lambda x: int(x * opacity))
    mark = Image.merge("RGBA", (r, g, b, a))
    out = Image.alpha_composite(base, mark)
    return out.convert("RGB")


def apply_transparency_watermark(img: Image.Image, wm: Image.Image, alpha: float = 0.30) -> Image.Image:
    base = np.array(img.convert("RGB"), dtype=np.float32)
    mark = np.array(wm.convert("RGB").resize(img.size, Image.LANCZOS), dtype=np.float32)
    blended = (1 - alpha) * base + alpha * mark
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))


def apply_additive_watermark(img: Image.Image, wm: Image.Image, strength: float = 0.15) -> Image.Image:
    base = np.array(img.convert("RGB"), dtype=np.float32)
    mark = np.array(wm.convert("RGB").resize(img.size, Image.LANCZOS), dtype=np.float32) / 255.0
    result = base + strength * mark * 255
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))


def apply_multiplicative_watermark(img: Image.Image, wm: Image.Image, strength: float = 0.20) -> Image.Image:
    base = np.array(img.convert("RGB"), dtype=np.float32)
    mark = np.array(wm.convert("L").resize(img.size, Image.LANCZOS), dtype=np.float32) / 255.0
    factor = 1.0 + strength * (mark - 0.5) * 2
    result = base * factor[..., np.newaxis]
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8))
