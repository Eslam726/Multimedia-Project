import numpy as np
from PIL import Image


def apply_hsi(img: Image.Image) -> Image.Image:
    """Convert RGB to HSI and return a false-colour visualisation."""
    rgb = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    intensity = (r + g + b) / 3.0
    saturation = 1 - 3 * np.minimum(np.minimum(r, g), b) / (r + g + b + 1e-8)
    num = 0.5 * ((r - g) + (r - b))
    den = np.sqrt((r - g) ** 2 + (r - b) * (g - b)) + 1e-8
    theta = np.arccos(np.clip(num / den, -1, 1))
    hue = np.where(b <= g, theta, 2 * np.pi - theta) / (2 * np.pi)
    hsi = np.stack([hue, saturation, intensity], axis=-1)
    hsi = (np.clip(hsi, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(hsi, mode="RGB")


def apply_hsi_watermark(img: Image.Image, wm: Image.Image, strength: float = 0.08) -> Image.Image:
    """Embed a watermark by perturbing the intensity component of the image."""
    rgb = np.array(img.convert("RGB"), dtype=np.float32) / 255.0
    wm_norm = np.array(wm.convert("L").resize(img.size, Image.LANCZOS), dtype=np.float32) / 255.0

    intensity = rgb.mean(axis=2)
    embedded_intensity = np.clip(intensity + strength * (wm_norm - 0.5), 0.0, 1.0)
    scale = embedded_intensity / (intensity + 1e-8)
    watermarked = np.clip(rgb * scale[..., np.newaxis], 0.0, 1.0)

    return Image.fromarray((watermarked * 255).astype(np.uint8), mode="RGB")
