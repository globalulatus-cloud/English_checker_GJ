"""Streamlit entry point:  streamlit run app.py"""
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

import settings as cfg
import ui
from analysis import analyse
from exporter import build_workbook
from mxliff_parser import MxliffError, Segment, parse_mxliff

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

st.set_page_config(page_title="MXLIFF Language Checker", page_icon="🔎", layout="wide")


@st.cache_data(show_spinner=False)
def load_segments(data: bytes) -> list[Segment]:
    return parse_mxliff(data)


def style_results(df: pd.DataFrame):
    def red(column: pd.Series) -> list[str]:
        return [
            "background-color:#D32F2F;color:white;font-weight:600"
            if pd.notna(v) and v < cfg.CONFIDENCE_THRESHOLD else ""
            for v in column
        ]
    return df.style.apply(red, subset=[cfg.COL_CONF]).format({cfg.COL_CONF: "{:.1%}"}, na_rep="")


def show_per_file(frames: list[tuple[str, pd.DataFrame]], render) -> None:
    if len(frames) == 1:
        render(frames[0][1])
        return
    for tab, (name, df) in zip(st.tabs([n for n, _ in frames]), frames):
        with tab:
            render(df)


def run_analysis(files: list[tuple[str, list[Segment]]], signature: tuple) -> None:
    grand_total = sum(len(segs) for _, segs in files)
    bar = st.progress(0.0, text="Reading between the lines…")
    frames, done_before = [], 0
    for name, segs in files:
        def update(i: int, _total: int, base: int = done_before) -> None:
            bar.progress((base + i) / grand_total, text=f"Analysing… {base + i} / {grand_total}")
        frames.append((name, analyse(segs, update)))
        done_before += len(segs)
    bar.empty()
    st.session_state["result"] = {
        "signature": signature,
        "frames": frames,
        "xlsx": build_workbook(frames),
    }
    st.toast("Analysis complete 🎉")


def main() -> None:
    ui.inject_styles()
    ui.hero()
    tracker = st.empty()

    uploads = st.file_uploader(
        "Upload MXLIFF files", type=["mxliff"], accept_multiple_files=True,
        help="One file or several. Each file becomes its own sheet in the Excel report.",
    )

    files, signature = [], []
    for upload in uploads:
        data = upload.getvalue()
        try:
            files.append((upload.name, load_segments(data)))
            signature.append((upload.name, hashlib.sha256(data).hexdigest()))
        except MxliffError as exc:
            st.error(f"**{upload.name}**: {exc}")
    signature = tuple(signature)

    result = st.session_state.get("result")
    fresh = bool(result) and result["signature"] == signature and bool(files)
    tracker.markdown(ui.step_tracker(3 if fresh else 2 if files else 1), unsafe_allow_html=True)

    if files:
        st.subheader(f"👀 Preview · first {cfg.PREVIEW_ROWS} segments")
        previews = [
            (name, pd.DataFrame(
                [(s.number, s.segment_id, s.source, s.target) for s in segs[: cfg.PREVIEW_ROWS]],
                columns=[cfg.COL_NUMBER, cfg.COL_ID, cfg.COL_SOURCE, cfg.COL_TARGET],
            ))
            for name, segs in files
        ]
        show_per_file(previews, lambda df: st.dataframe(df, hide_index=True, width="stretch"))
        st.caption(" · ".join(f"{name}: {len(segs):,} segments" for name, segs in files))

    if st.button("⚡ Analyse segments", type="primary", disabled=not files):
        run_analysis(files, signature)
        st.rerun()

    if result and not fresh and files:
        st.info("The uploaded files changed. Press **Analyse segments** to refresh the report.")

    if fresh:
        frames = result["frames"]
        all_rows = pd.concat([df for _, df in frames])
        confidence = all_rows[cfg.COL_CONF]
        st.subheader("📊 Results")
        ui.stat_cards([
            ("Segments analysed", len(all_rows), "#00E5FF"),
            ("Source and target both English", int((all_rows[cfg.COL_BOTH_EN] == "Yes").sum()), "#FFB703"),
            (f"Confidence below {cfg.CONFIDENCE_THRESHOLD:.0%}",
             int((confidence < cfg.CONFIDENCE_THRESHOLD).sum()), "#FF4D5A"),
        ])
        show_per_file(frames, lambda df: st.dataframe(style_results(df), hide_index=True, width="stretch"))

        stem = Path(frames[0][0]).stem if len(frames) == 1 else "mxliff"
        st.download_button(
            "⬇️ Download Excel report", data=result["xlsx"],
            file_name=f"{stem}_language_check.xlsx", mime=XLSX_MIME, type="primary",
        )


main()
