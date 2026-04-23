import numpy as np
from PIL import Image


def apply_lsb_substitution(img: Image.Image, wm: Image.Image) -> Image.Image:
    """Embed watermark in LSB of the host image."""
    host = np.array(img.convert("RGB"))
    wm_r = np.array(wm.convert("L").resize((host.shape[1], host.shape[0]), Image.LANCZOS))
    wm_bits = (wm_r > 127).astype(np.uint8)
    stego = host.copy()
    stego[..., 0] = (host[..., 0] & 0xFE) | wm_bits
    return Image.fromarray(stego.astype(np.uint8))


def apply_lsb_matching(img: Image.Image, wm: Image.Image) -> Image.Image:
    """LSB matching steganography (+/-1 embedding)."""
    host = np.array(img.convert("RGB")).astype(int)
    wm_r = np.array(wm.convert("L").resize((host.shape[1], host.shape[0]), Image.LANCZOS))
    wm_bits = (wm_r > 127).astype(int)
    lsb = host[..., 0] & 1
    delta = wm_bits - lsb
    rng = np.random.default_rng(42)
    adj = np.where(delta != 0, rng.choice([-1, 1], size=delta.shape), 0)
    stego = host.copy()
    stego[..., 0] = np.clip(host[..., 0] + adj, 0, 255)
    return Image.fromarray(stego.astype(np.uint8))
