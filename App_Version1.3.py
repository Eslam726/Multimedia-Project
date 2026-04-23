import streamlit as st
from PIL import Image
import io
import time
from image_ops import *
from Style import SHARED_CSS

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Image Processing & Watermarking Tool",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FUNCTION CATALOGUE
# ─────────────────────────────────────────────
FUNCTIONS_NO_WM = [
    "DCT – Discrete Cosine Transform",
    "DWT – Discrete Wavelet Transform",
    "HSI Conversion",
    "LBP – Local Binary Pattern",
    "Image Resize",
    "Scaling",
    "Cropping",
    "Rotation",
]
FUNCTIONS_WM_ONLY = [
    "LSB Substitution",
    "LSB Matching",
    "DCT Watermark Embedding",
    "DWT Watermark Embedding",
    "HSI Watermark Embedding",
    "LBP Watermark Embedding",
    "Add Visible Watermark",
    "Transparency Watermark Overlaying",
    "Additive Watermark Overlaying",
    "Multiplicative Watermark Overlaying",
]

TOOLTIPS = {
    "DCT – Discrete Cosine Transform":     "Visualises the frequency-domain representation of the image using 2D DCT.",
    "DWT – Discrete Wavelet Transform":    "Decomposes the image into four Haar sub-bands (LL, LH, HL, HH).",
    "HSI Conversion":                      "Converts the image from RGB colour space to Hue–Saturation–Intensity.",
    "LBP – Local Binary Pattern":          "Extracts rotation-invariant texture features using the LBP descriptor.",
    "Image Resize":                        "Resizes the image to a specified width × height.",
    "Scaling":                             "Scales the image up or down by a percentage factor.",
    "Cropping":                            "Crops a rectangular region from the image.",
    "Rotation":                            "Rotates the image by an arbitrary angle.",
    "LSB Substitution":                    "Hides the watermark in the least-significant bits of the host image.",
    "LSB Matching":                        "Embeds watermark bits via ±1 pixel adjustments for lower distortion.",
    "DCT Watermark Embedding":             "Embeds the watermark into mid-frequency DCT coefficients of 8x8 luminance blocks.",
    "DWT Watermark Embedding":             "Embeds the watermark into low-frequency Haar wavelet coefficients.",
    "HSI Watermark Embedding":             "Embeds the watermark by perturbing the image intensity in HSI space.",
    "LBP Watermark Embedding":             "Embeds the watermark only in texture-rich regions selected from the LBP map.",
    "Add Visible Watermark":               "Composites the watermark on top of the host image at adjustable opacity.",
    "Transparency Watermark Overlaying":   "Blends the watermark with the host image using alpha compositing.",
    "Additive Watermark Overlaying":       "Adds the watermark signal to the host image additively.",
    "Multiplicative Watermark Overlaying": "Modulates the host image by the watermark signal multiplicatively.",
}

# ─────────────────────────────────────────────
#  INIT SESSION STATE
# ─────────────────────────────────────────────
if "output_images" not in st.session_state:
    st.session_state["output_images"] = []   # list of dicts: {img, label, timestamp}
if "result_img" not in st.session_state:
    st.session_state["result_img"] = None

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem 0;'>
        <div style='font-family: Syne, sans-serif; font-size: 1.4rem; font-weight: 800;
                    color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.2;'>
            🖼️ ImgProc<span style='color: #FF6B1A;'>Studio</span>
        </div>
        <div style='font-size: 0.78rem; color: #8FA0B0; margin-top: 4px; font-weight: 300;'>
            Processing & Watermarking
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Upload Main Image ──
    st.markdown("**📁 Main Image**")
    uploaded_main = st.file_uploader(
        "Upload main image", type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        key="main_img", label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Upload Watermark ──
    st.markdown("**🔖 Watermark Image** *(optional)*")
    uploaded_wm = st.file_uploader(
        "Upload watermark", type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        key="wm_img", label_visibility="collapsed"
    )

    if uploaded_wm:
        st.markdown('<span class="badge badge-orange">✓ Watermark loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-blue">No watermark</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Function Selector ──
    available = FUNCTIONS_NO_WM + (FUNCTIONS_WM_ONLY if uploaded_wm else [])
    st.markdown("**⚙️ Select Function**")
    selected_fn = st.selectbox("Function", available, label_visibility="collapsed")

    if selected_fn in TOOLTIPS:
        st.caption(f"ℹ️ {TOOLTIPS[selected_fn]}")

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    if not uploaded_wm:
        st.info("Upload a watermark to unlock 10 additional embedding functions.")

    st.markdown("---")

    # ── Video page link indicator ──
    n_imgs = len(st.session_state["output_images"])
    if n_imgs > 0:
        st.markdown(f"""
        <div style='background: rgba(255,107,26,0.15); border: 1px solid rgba(255,107,26,0.4);
                    border-radius: 10px; padding: 0.8rem 1rem; margin-top: 0.5rem;'>
            <div style='font-family: Syne, sans-serif; font-weight: 700; color: #FF8C4A;
                        font-size: 0.85rem;'>🎬 Video Generator</div>
            <div style='font-size: 0.78rem; color: #B8C5D3; margin-top: 3px;'>
                {n_imgs} image{"s" if n_imgs != 1 else ""} saved · go to <b>Video Generator</b> page
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN AREA – HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>Image Processing &<br><span>Watermarking</span> Tool</div>
<div class='hero-subtitle'>Transform, analyse, and protect your images with precision.</div>
""", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PREVIEWS
# ─────────────────────────────────────────────
if uploaded_main or uploaded_wm:
    prev_cols = st.columns([1, 1] if uploaded_wm else [1])
    if uploaded_main:
        with prev_cols[0]:
            st.markdown("<div class='card'><div class='card-header'>Main Image Preview</div>", unsafe_allow_html=True)
            main_img = Image.open(uploaded_main)
            st.image(main_img, use_container_width=True,
                     caption=f"{main_img.size[0]}×{main_img.size[1]} px · {main_img.mode}")
            st.markdown("</div>", unsafe_allow_html=True)
    if uploaded_wm:
        with prev_cols[1]:
            st.markdown("<div class='card'><div class='card-header'>Watermark Preview</div>", unsafe_allow_html=True)
            wm_img = Image.open(uploaded_wm)
            st.image(wm_img, use_container_width=True,
                     caption=f"{wm_img.size[0]}×{wm_img.size[1]} px · {wm_img.mode}")
            st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PARAMETERS & PROCESS BUTTON
# ─────────────────────────────────────────────
if not uploaded_main:
    st.markdown("""
    <div class='card' style='text-align:center; padding: 3rem 2rem;'>
        <div style='font-size:3rem; margin-bottom:1rem;'>📂</div>
        <div style='font-family: Syne, sans-serif; font-size:1.2rem; font-weight:700;
                    color: #0D1B2A;'>No image uploaded yet</div>
        <div style='color: #6B7A8D; margin-top:0.4rem;'>
            Use the sidebar to upload a main image to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Per-function parameter widgets ──
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown(f"<div class='card-header'>Parameters — {selected_fn}</div>", unsafe_allow_html=True)

params = {}

if selected_fn == "Image Resize":
    w, h = main_img.size
    c1, c2 = st.columns(2)
    params["width"]  = c1.number_input("Width (px)",  min_value=10, max_value=8000, value=w)
    params["height"] = c2.number_input("Height (px)", min_value=10, max_value=8000, value=h)

elif selected_fn == "Scaling":
    params["factor"] = st.slider("Scale Factor", 0.1, 5.0, 1.0, 0.05, format="%.2f×")

elif selected_fn == "Cropping":
    w, h = main_img.size
    c1, c2, c3, c4 = st.columns(4)
    params["left"]   = c1.number_input("Left",   0, w-2,  0)
    params["top"]    = c2.number_input("Top",    0, h-2,  0)
    params["right"]  = c3.number_input("Right",  2, w,    w)
    params["bottom"] = c4.number_input("Bottom", 2, h,    h)

elif selected_fn == "Rotation":
    c1, c2 = st.columns(2)
    params["angle"]  = c1.slider("Angle (°)", -180, 180, 0)
    params["expand"] = c2.checkbox("Expand canvas", value=True)

elif selected_fn == "LBP – Local Binary Pattern":
    c1, c2 = st.columns(2)
    params["radius"]   = c1.slider("Radius",   1, 10, 3)
    params["n_points"] = c2.slider("N Points", 8, 48, 24, 8)

elif selected_fn == "DCT Watermark Embedding":
    params["strength"] = st.slider("DCT Strength", 1.0, 100.0, 25.0, 1.0)

elif selected_fn == "DWT Watermark Embedding":
    params["strength"] = st.slider("DWT Strength", 1.0, 50.0, 8.0, 1.0)

elif selected_fn == "HSI Watermark Embedding":
    params["strength"] = st.slider("HSI Strength", 0.01, 0.50, 0.08, 0.01)

elif selected_fn == "LBP Watermark Embedding":
    c1, c2 = st.columns(2)
    params["radius"]   = c1.slider("Radius",   1, 10, 3)
    params["n_points"] = c2.slider("N Points", 8, 48, 24, 8)

elif selected_fn in ("Add Visible Watermark",):
    params["opacity"] = st.slider("Watermark Opacity", 0.05, 1.0, 0.55, 0.05)

elif selected_fn == "Transparency Watermark Overlaying":
    params["alpha"] = st.slider("Blend Alpha", 0.0, 1.0, 0.30, 0.05)

elif selected_fn == "Additive Watermark Overlaying":
    params["strength"] = st.slider("Strength", 0.01, 1.0, 0.15, 0.01)

elif selected_fn == "Multiplicative Watermark Overlaying":
    params["strength"] = st.slider("Strength", 0.01, 1.0, 0.20, 0.01)

else:
    st.caption("No adjustable parameters for this function.")

st.markdown("</div>", unsafe_allow_html=True)

# ── Process Button ──
col_btn, _ = st.columns([1, 3])
run = col_btn.button("▶  Process Image", use_container_width=True)

# ─────────────────────────────────────────────
#  PROCESSING
# ─────────────────────────────────────────────
if run:
    if selected_fn in FUNCTIONS_WM_ONLY and not uploaded_wm:
        st.error("⚠️ This function requires a watermark image. Please upload one in the sidebar.")
        st.stop()

    with st.spinner("Processing…"):
        time.sleep(0.3)
        try:
            result_img = None
            wm_pil = Image.open(uploaded_wm) if uploaded_wm else None

            if selected_fn == "DCT – Discrete Cosine Transform":
                result_img = apply_dct(main_img)
            elif selected_fn == "DWT – Discrete Wavelet Transform":
                result_img = apply_dwt(main_img)
            elif selected_fn == "HSI Conversion":
                result_img = apply_hsi(main_img)
            elif selected_fn == "LBP – Local Binary Pattern":
                result_img = apply_lbp(main_img, params["radius"], params["n_points"])
            elif selected_fn == "DCT Watermark Embedding":
                result_img = apply_dct_watermark(main_img, wm_pil, params["strength"])
            elif selected_fn == "DWT Watermark Embedding":
                result_img = apply_dwt_watermark(main_img, wm_pil, params["strength"])
            elif selected_fn == "HSI Watermark Embedding":
                result_img = apply_hsi_watermark(main_img, wm_pil, params["strength"])
            elif selected_fn == "LBP Watermark Embedding":
                result_img = apply_lbp_watermark(main_img, wm_pil, params["radius"], params["n_points"])
            elif selected_fn == "Image Resize":
                result_img = apply_resize(main_img, params["width"], params["height"])
            elif selected_fn == "Scaling":
                result_img = apply_scale(main_img, params["factor"])
            elif selected_fn == "Cropping":
                result_img = apply_crop(main_img, params["left"], params["top"],
                                        params["right"], params["bottom"])
            elif selected_fn == "Rotation":
                result_img = apply_rotation(main_img, params["angle"], params["expand"])
            elif selected_fn == "LSB Substitution":
                result_img = apply_lsb_substitution(main_img, wm_pil)
            elif selected_fn == "LSB Matching":
                result_img = apply_lsb_matching(main_img, wm_pil)
            elif selected_fn == "Add Visible Watermark":
                result_img = apply_visible_watermark(main_img, wm_pil, params["opacity"])
            elif selected_fn == "Transparency Watermark Overlaying":
                result_img = apply_transparency_watermark(main_img, wm_pil, params["alpha"])
            elif selected_fn == "Additive Watermark Overlaying":
                result_img = apply_additive_watermark(main_img, wm_pil, params["strength"])
            elif selected_fn == "Multiplicative Watermark Overlaying":
                result_img = apply_multiplicative_watermark(main_img, wm_pil, params["strength"])

            st.session_state["result_img"] = result_img

            # ── Auto-save to video queue ──
            if result_img is not None:
                import datetime
                st.session_state["output_images"].append({
                    "img":       result_img.copy(),
                    "label":     selected_fn,
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                })

        except Exception as e:
            st.error(f"❌ Processing failed: {e}")
            st.stop()

# ─────────────────────────────────────────────
#  OUTPUT
# ─────────────────────────────────────────────
if st.session_state["result_img"] is not None:
    result = st.session_state["result_img"]
    st.markdown("---")
    st.markdown("""
    <div style='font-family: Syne, sans-serif; font-size:1.15rem; font-weight:700;
                color: #0D1B2A; margin-bottom:0.8rem;'>
        ✅ Processed Output
    </div>
    """, unsafe_allow_html=True)

    out_col, info_col = st.columns([3, 1])

    with out_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image(result, use_container_width=True,
                 caption=f"Result — {result.size[0]}×{result.size[1]} px")
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>Image Info</div>", unsafe_allow_html=True)
        orig_w, orig_h = main_img.size
        new_w,  new_h  = result.size
        st.metric("Width",  f"{new_w} px", delta=f"{new_w - orig_w:+d}")
        st.metric("Height", f"{new_h} px", delta=f"{new_h - orig_h:+d}")
        st.metric("Mode",   result.mode)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>Download</div>", unsafe_allow_html=True)

        fmt  = st.selectbox("Format", ["PNG", "JPEG", "BMP", "TIFF"], key="dl_fmt")
        mime = {"PNG": "image/png", "JPEG": "image/jpeg",
                "BMP": "image/bmp", "TIFF": "image/tiff"}[fmt]

        st.download_button(
            label="⬇ Download",
            data=img_to_bytes(result, fmt),
            file_name=f"processed.{fmt.lower()}",
            mime=mime,
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Video queue hint ──
        n = len(st.session_state["output_images"])
        if n > 0:
            st.markdown(f"""
            <div style='margin-top:0.8rem; background:#E8F5EE; border:1px solid #A8D8BC;
                        border-radius:10px; padding:0.8rem 1rem; text-align:center;'>
                <div style='font-family:Syne,sans-serif; font-weight:700; color:#1A7A45;
                            font-size:0.85rem;'>🎬 {n} frame{"s" if n!=1 else ""} queued</div>
                <div style='font-size:0.75rem; color:#3A7A55; margin-top:2px;'>
                    Open <b>Video Generator</b> page to create your video
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("🔍 Side-by-side Comparison", expanded=False):
        c1, c2 = st.columns(2)
        c1.image(main_img,  caption="Original",  use_container_width=True)
        c2.image(result,    caption="Processed", use_container_width=True)