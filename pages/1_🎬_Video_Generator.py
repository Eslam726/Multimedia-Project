import streamlit as st
import numpy as np
from PIL import Image
import io
import time
import sys
import os

# ── Allow imports from parent directory ──
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from Style import SHARED_CSS

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Video Generator — ImgProcStudio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPER – PIL image → bytes
# ─────────────────────────────────────────────
def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format=fmt)
    return buf.getvalue()


def make_video(frames, fps: int, size: tuple) -> bytes:
    """Build an MP4 video from a list of PIL images using imageio/opencv."""
    import imageio
    buf = io.BytesIO()
    with imageio.get_writer(buf, format="mp4", fps=fps, codec="libx264",
                             output_params=["-pix_fmt", "yuv420p"]) as writer:
        for frame in frames:
            arr = np.array(frame.convert("RGB").resize(size, Image.LANCZOS))
            writer.append_data(arr)
    return buf.getvalue()


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

    # ── Video settings ──
    st.markdown("**🎬 Video Settings**")

    fps = st.slider("Frames Per Second (FPS)", min_value=1, max_value=30, value=3,
                    help="Higher FPS = smoother but faster video")

    out_w = st.number_input("Output Width (px)",  min_value=64, max_value=3840, value=640)
    out_h = st.number_input("Output Height (px)", min_value=64, max_value=2160, value=480)

    st.markdown("---")

    # ── Frame queue info ──
    n_frames = len(st.session_state.get("output_images", []))
    st.markdown(f"""
    <div style='background: rgba(255,107,26,0.12); border: 1px solid rgba(255,107,26,0.35);
                border-radius: 10px; padding: 0.8rem 1rem;'>
        <div style='font-family: Syne, sans-serif; font-weight: 700; color: #FF8C4A;
                    font-size: 0.9rem;'>🖼️ Frame Queue</div>
        <div style='font-size: 1.6rem; font-weight: 800; color: #FFFFFF;
                    font-family: Syne, sans-serif; margin: 4px 0;'>{n_frames}</div>
        <div style='font-size: 0.75rem; color: #B8C5D3;'>
            image{"s" if n_frames != 1 else ""} collected from processing
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

    # ── Clear queue button ──
    if n_frames > 0:
        if st.button("🗑️  Clear Frame Queue", use_container_width=True):
            st.session_state["output_images"] = []
            st.session_state.pop("generated_video", None)
            st.rerun()


# ─────────────────────────────────────────────
#  MAIN AREA – HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>🎬 Video <span>Generator</span></div>
<div class='hero-subtitle'>Turn your processed output images into a smooth video sequence.</div>
""", unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  EMPTY STATE
# ─────────────────────────────────────────────
output_images = st.session_state.get("output_images", [])

if not output_images:
    st.markdown("""
    <div class='card' style='text-align:center; padding: 3.5rem 2rem;'>
        <div style='font-size:3.5rem; margin-bottom:1rem;'>🎞️</div>
        <div style='font-family: Syne, sans-serif; font-size:1.25rem; font-weight:700;
                    color: #0D1B2A;'>No frames collected yet</div>
        <div style='color: #6B7A8D; margin-top:0.5rem; max-width:400px; margin-inline:auto;'>
            Process images on the <b>main page</b> — each result is automatically
            added to the video queue. Come back here when you have frames ready.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  FRAME GALLERY
# ─────────────────────────────────────────────
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown(f"<div class='card-header'>Frame Queue — {len(output_images)} frame{'s' if len(output_images)!=1 else ''}</div>",
            unsafe_allow_html=True)

# Show thumbnails in a grid (up to 12 shown, rest summarised)
MAX_SHOWN = 12
shown = output_images[:MAX_SHOWN]
cols = st.columns(min(len(shown), 6))

for i, entry in enumerate(shown):
    with cols[i % 6]:
        st.image(
            entry["img"],
            use_container_width=True,
            caption=f"#{i+1} · {entry['label'][:18]}{'…' if len(entry['label'])>18 else ''}\n{entry['timestamp']}",
        )

if len(output_images) > MAX_SHOWN:
    st.caption(f"… and {len(output_images) - MAX_SHOWN} more frame(s) not shown.")

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  REORDER / REMOVE FRAMES
# ─────────────────────────────────────────────
with st.expander("⚙️  Manage Frames", expanded=False):
    st.caption("Select frames to remove from the queue, or reverse the order.")

    rm_col, rev_col = st.columns(2)

    with rm_col:
        labels = [f"#{i+1} — {e['label']} ({e['timestamp']})"
                  for i, e in enumerate(output_images)]
        to_remove = st.multiselect("Remove frames", options=labels, key="rm_frames")
        if st.button("Remove selected", key="btn_rm"):
            indices_to_rm = {labels.index(l) for l in to_remove}
            st.session_state["output_images"] = [
                e for i, e in enumerate(output_images) if i not in indices_to_rm
            ]
            st.session_state.pop("generated_video", None)
            st.rerun()

    with rev_col:
        st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)
        if st.button("🔃  Reverse frame order", key="btn_rev"):
            st.session_state["output_images"] = list(reversed(output_images))
            st.session_state.pop("generated_video", None)
            st.rerun()

# ─────────────────────────────────────────────
#  VIDEO GENERATION
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='font-family: Syne, sans-serif; font-size:1.15rem; font-weight:700;
            color: #0D1B2A; margin-bottom:0.8rem;'>
    🎬 Create Video
</div>
""", unsafe_allow_html=True)

gen_col, info_col = st.columns([2, 1])

with gen_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>Generation Settings Summary</div>", unsafe_allow_html=True)

    duration_sec = len(output_images) / fps
    m1, m2, m3 = st.columns(3)
    m1.metric("Frames",      len(output_images))
    m2.metric("FPS",         fps)
    m3.metric("Duration",    f"{duration_sec:.1f}s")

    mc1, mc2 = st.columns(2)
    mc1.metric("Output Width",  f"{out_w} px")
    mc2.metric("Output Height", f"{out_h} px")

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── BIG CREATE BUTTON ──
    create = st.button("🎬  Create Video from Output Images",
                       use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

with info_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>How It Works</div>", unsafe_allow_html=True)
    st.markdown("""
    <ol style='padding-left:1.1rem; color:#4A5568; font-size:0.88rem; line-height:1.8;'>
        <li>Each processed result is <b>auto-queued</b> as a frame.</li>
        <li>Adjust FPS &amp; resolution in the sidebar.</li>
        <li>Click <b>Create Video</b> to render the MP4.</li>
        <li>Preview &amp; download directly from this page.</li>
    </ol>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PROCESS VIDEO CREATION
# ─────────────────────────────────────────────
if create:
    with st.spinner("🎬 Rendering video — please wait…"):
        try:
            frames = [entry["img"] for entry in output_images]
            video_bytes = make_video(frames, fps=fps, size=(int(out_w), int(out_h)))
            st.session_state["generated_video"] = video_bytes
            st.success(f"✅ Video created successfully — {len(frames)} frames at {fps} FPS!")
        except Exception as e:
            st.error(f"❌ Video generation failed: {e}")
            st.info("💡 Make sure `imageio[ffmpeg]` is installed: `pip install imageio[ffmpeg]`")

# ─────────────────────────────────────────────
#  VIDEO PREVIEW & DOWNLOAD
# ─────────────────────────────────────────────
if "generated_video" in st.session_state and st.session_state["generated_video"]:
    video_bytes = st.session_state["generated_video"]

    st.markdown("---")
    st.markdown("""
    <div style='font-family: Syne, sans-serif; font-size:1.15rem; font-weight:700;
                color: #0D1B2A; margin-bottom:0.8rem;'>
        ▶ Video Preview
    </div>
    """, unsafe_allow_html=True)

    preview_col, dl_col = st.columns([3, 1])

    with preview_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>Preview</div>", unsafe_allow_html=True)
        st.video(video_bytes)
        st.markdown("</div>", unsafe_allow_html=True)

    with dl_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>Download</div>", unsafe_allow_html=True)

        size_kb = len(video_bytes) / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        st.metric("File Size", size_str)
        st.metric("Frames",    len(output_images))
        st.metric("FPS",       fps)

        st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇ Download MP4",
            data=video_bytes,
            file_name="imgproc_video.mp4",
            mime="video/mp4",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
