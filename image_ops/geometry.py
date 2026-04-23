from PIL import Image


def apply_resize(img: Image.Image, width: int, height: int) -> Image.Image:
    return img.resize((width, height), Image.LANCZOS)


def apply_scale(img: Image.Image, factor: float) -> Image.Image:
    w, h = img.size
    return img.resize((int(w * factor), int(h * factor)), Image.LANCZOS)


def apply_crop(img: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    w, h = img.size
    right = min(right, w)
    bottom = min(bottom, h)
    return img.crop((left, top, right, bottom))


def apply_rotation(img: Image.Image, angle: float, expand: bool = True) -> Image.Image:
    return img.rotate(angle, expand=expand, resample=Image.BICUBIC)
