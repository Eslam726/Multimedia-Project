import numpy as np
import pywt
from PIL import Image
from scipy.fftpack import dct, idct


def apply_dct(img: Image.Image) -> Image.Image:
    """Apply 2D DCT and visualise the log-magnitude spectrum."""
    gray = np.array(img.convert("L"), dtype=np.float32)
    dct2 = dct(dct(gray, axis=0, norm="ortho"), axis=1, norm="ortho")
    log_dct = np.log(np.abs(dct2) + 1)
    norm = ((log_dct - log_dct.min()) / (np.ptp(log_dct) + 1e-8) * 255).astype(np.uint8)
    return Image.fromarray(norm).convert("RGB")


def apply_dwt(img: Image.Image) -> Image.Image:
    """Apply one-level 2D DWT (Haar) and tile the four sub-bands."""
    gray = np.array(img.convert("L"), dtype=np.float32)
    ll, (lh, hl, hh) = pywt.dwt2(gray, "haar")

    def norm(a):
        a = np.abs(a)
        return ((a - a.min()) / (np.ptp(a) + 1e-8) * 255).astype(np.uint8)

    top = np.hstack([norm(ll), norm(lh)])
    bottom = np.hstack([norm(hl), norm(hh)])
    tiled = np.vstack([top, bottom])
    return Image.fromarray(tiled).convert("RGB")


def apply_dct_watermark(img: Image.Image, wm: Image.Image, strength: float = 25.0) -> Image.Image:
    """Embed a watermark by modifying one mid-band DCT coefficient per 8x8 block."""
    ycbcr = np.array(img.convert("YCbCr"), dtype=np.float32)
    y_channel = ycbcr[..., 0]

    wm_gray = wm.convert("L").resize(img.size, Image.LANCZOS)
    wm_bits = (np.array(wm_gray, dtype=np.uint8) > 127).astype(np.float32)

    h, w = y_channel.shape
    block_size = 8
    watermarked = y_channel.copy()

    for row in range(0, h - (h % block_size), block_size):
        for col in range(0, w - (w % block_size), block_size):
            block = watermarked[row:row + block_size, col:col + block_size]
            block_dct = dct(dct(block, axis=0, norm="ortho"), axis=1, norm="ortho")
            bit = wm_bits[row:row + block_size, col:col + block_size].mean() >= 0.5
            coeff = block_dct[4, 4]
            block_dct[4, 4] = abs(coeff) + strength if bit else -abs(coeff) - strength
            block_idct = idct(idct(block_dct, axis=0, norm="ortho"), axis=1, norm="ortho")
            watermarked[row:row + block_size, col:col + block_size] = block_idct

    ycbcr[..., 0] = np.clip(watermarked, 0, 255)
    return Image.fromarray(ycbcr.astype(np.uint8), mode="YCbCr").convert("RGB")


def apply_dwt_watermark(img: Image.Image, wm: Image.Image, strength: float = 8.0) -> Image.Image:
    """Embed a watermark in the low-frequency Haar wavelet coefficients."""
    ycbcr = np.array(img.convert("YCbCr"), dtype=np.float32)
    y_channel = ycbcr[..., 0]

    ll, (lh, hl, hh) = pywt.dwt2(y_channel, "haar")
    wm_small = wm.convert("L").resize((ll.shape[1], ll.shape[0]), Image.LANCZOS)
    wm_centered = np.array(wm_small, dtype=np.float32) / 255.0 - 0.5

    ll_embedded = ll + strength * wm_centered
    reconstructed = pywt.idwt2((ll_embedded, (lh, hl, hh)), "haar")
    reconstructed = reconstructed[: y_channel.shape[0], : y_channel.shape[1]]

    ycbcr[..., 0] = np.clip(reconstructed, 0, 255)
    return Image.fromarray(ycbcr.astype(np.uint8), mode="YCbCr").convert("RGB")
