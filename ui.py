"""Look and feel: CSS, hero banner, step tracker and stat cards."""
from html import escape

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Exo+2:wght@400;500;700&display=swap');
.stApp {
  font-family: 'Exo 2', system-ui, sans-serif;
  background:
    radial-gradient(900px 500px at 90% -5%, rgba(0,229,255,.16), transparent 60%),
    linear-gradient(rgba(0,229,255,.05) 1px, transparent 1px) 0 0 / 44px 44px,
    linear-gradient(90deg, rgba(0,229,255,.05) 1px, transparent 1px) 0 0 / 44px 44px,
    #060D1A;
}
.block-container { max-width: 1100px; padding-top: 4.5rem; }
.stApp h2, .stApp h3 { font-family: 'Orbitron', 'Exo 2', sans-serif; font-weight: 600; letter-spacing: .02em; }

.hero { display: flex; align-items: center; justify-content: space-between; gap: 2rem; flex-wrap: wrap; margin-bottom: 1.2rem; }
.hero > div:first-child { flex: 1 1 420px; min-width: 0; }
.hero h1 { font-family: 'Orbitron', 'Exo 2', sans-serif; font-weight: 800; letter-spacing: .01em;
  font-size: clamp(1.6rem, 4vw, 2.5rem); line-height: 1.15; margin: 0 0 .7rem; color: #FFFFFF;
  text-shadow: 0 0 18px rgba(0,229,255,.45); }
.hero p { color: #A9C7DD; max-width: 56ch; margin: 0 0 1rem; font-size: 1.05rem; }
.tags { display: flex; gap: .5rem; flex-wrap: wrap; }
.tag { font-family: 'Orbitron', monospace; font-size: .8rem; padding: .2rem .7rem; color: #00E5FF;
  border: 1px solid rgba(0,229,255,.6); background: rgba(0,229,255,.08); border-radius: 4px; }
.tag.alert { color: #FFB703; border-color: rgba(255,183,3,.7); background: rgba(255,183,3,.08); }

.reactor { position: relative; width: 140px; height: 140px; flex: none; margin-right: 1rem; }
.reactor i { position: absolute; border-radius: 50%; }
.reactor i:nth-child(1) { inset: 0; border: 3px solid #00E5FF;
  box-shadow: 0 0 22px rgba(0,229,255,.55), inset 0 0 22px rgba(0,229,255,.35); }
.reactor i:nth-child(2) { inset: 18px; border: 10px dotted rgba(0,229,255,.75); }
.reactor i:nth-child(3) { inset: 48px; box-shadow: 0 0 30px 6px rgba(0,229,255,.6);
  background: radial-gradient(circle, #FFFFFF 0, #BFF6FF 35%, #00E5FF 75%, rgba(0,229,255,0) 100%); }
@media (prefers-reduced-motion: no-preference) {
  .reactor i:nth-child(2) { animation: reactor-spin 16s linear infinite; }
  @keyframes reactor-spin { to { transform: rotate(360deg); } }
}

.steps { display: flex; gap: .75rem; flex-wrap: wrap; margin-bottom: 1.6rem; }
.step { display: flex; align-items: center; gap: .55rem; padding: .45rem 1.1rem .45rem .5rem; border-radius: 4px;
  border: 1px solid #25476D; background: #0F2038; color: #7F9BB8; font-weight: 500; }
.step b { display: grid; place-items: center; width: 1.6rem; height: 1.6rem; border-radius: 3px;
  background: #16304F; font-family: 'Orbitron', monospace; font-size: .8rem; }
.step.active { border-color: #FFB703; color: #FFFFFF; box-shadow: 0 0 16px rgba(255,183,3,.25); }
.step.active b { background: #FFB703; color: #060D1A; }
.step.done { border-color: #00E5FF; color: #00E5FF; }
.step.done b { background: #00E5FF; color: #060D1A; }

[data-testid="stFileUploaderDropzone"] { border: 2px dashed #00E5FF; border-radius: 10px; background: #0F2038; }
[data-testid="stDataFrame"] { border: 1px solid rgba(0,229,255,.55); border-radius: 10px; overflow: hidden;
  box-shadow: 0 0 26px rgba(0,229,255,.14); }
.stButton > button, [data-testid="stDownloadButton"] button { border-radius: 6px; padding: .6rem 1.4rem;
  font-family: 'Orbitron', 'Exo 2', sans-serif; font-weight: 600; letter-spacing: .03em;
  box-shadow: 0 0 18px rgba(0,229,255,.35); }
.stButton > button:disabled { box-shadow: none; }
[data-baseweb="tab"] { font-weight: 700; }

.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin: .5rem 0 1.5rem; }
.stat { background: #0F2038; padding: 1.1rem 1.3rem; border: 1px solid #25476D; border-left: 6px solid var(--tone);
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 16px), calc(100% - 16px) 100%, 0 100%); }
.stat .v { font-family: 'Orbitron', 'Exo 2', sans-serif; font-size: 2.2rem; font-weight: 800; line-height: 1.15;
  color: var(--tone); text-shadow: 0 0 14px var(--tone); }
.stat .l { color: #A9C7DD; }
</style>
"""

_STEPS = ("Upload", "Analyse", "Download")


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <div>
            <h1>Which language is hiding in your segments?</h1>
            <p>Drop in MXLIFF files and get an Excel report that shows the language of every
            source and target, and flags the ones the detector is unsure about.</p>
            <div class="tags"><span class="tag">fi</span><span class="tag">en</span>
            <span class="tag">sv</span><span class="tag">de</span><span class="tag alert">?</span></div>
          </div>
          <div class="reactor" aria-hidden="true"><i></i><i></i><i></i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def step_tracker(active: int) -> str:
    """HTML for the 3-step tracker; steps before `active` (1-3) show as done."""
    items = []
    for number, label in enumerate(_STEPS, start=1):
        state = "done" if number < active else "active" if number == active else ""
        mark = "✓" if state == "done" else str(number)
        items.append(f'<div class="step {state}"><b>{mark}</b>{escape(label)}</div>')
    return f'<div class="steps">{"".join(items)}</div>'


def stat_cards(cards: list[tuple[str, int, str]]) -> None:
    """Render (label, value, colour) cards."""
    html = "".join(
        f'<div class="stat" style="--tone:{escape(tone)}"><div class="v">{int(value):,}</div>'
        f'<div class="l">{escape(label)}</div></div>'
        for label, value, tone in cards
    )
    st.markdown(f'<div class="stats">{html}</div>', unsafe_allow_html=True)
