import numpy as np
from PIL import Image
from skimage.feature import local_binary_pattern


def apply_lbp(img: Image.Image, radius: int = 3, n_points: int = 24) -> Image.Image:
    """Compute Local Binary Pattern texture descriptor."""
    gray = np.array(img.convert("L"))
    lbp = local_binary_pattern(gray, n_points, radius, method="uniform")
    lbp_norm = ((lbp - lbp.min()) / (np.ptp(lbp) + 1e-8) * 255).astype(np.uint8)
    return Image.fromarray(lbp_norm).convert("RGB")


def apply_lbp_watermark(
    img: Image.Image,
    wm: Image.Image,
    radius: int = 3,
    n_points: int = 24,
) -> Image.Image:
    """Embed a watermark in texture-rich regions selected from the LBP map."""
    host = np.array(img.convert("RGB"), dtype=np.uint8)
    gray = np.array(img.convert("L"), dtype=np.uint8)
    wm_bits = (
        np.array(wm.convert("L").resize((host.shape[1], host.shape[0]), Image.LANCZOS), dtype=np.uint8) > 127
    ).astype(np.uint8)

    lbp = local_binary_pattern(gray, n_points, radius, method="uniform")
    texture_mask = lbp >= np.median(lbp)

    watermarked = host.copy()
    blue_channel = watermarked[..., 2]
    blue_channel[texture_mask] = (blue_channel[texture_mask] & 0xFE) | wm_bits[texture_mask]

    return Image.fromarray(watermarked, mode="RGB")
