import streamlit as st
import time
import pandas as pd
import numpy as np
import random
from io import BytesIO
from fpdf import FPDF
import pyttsx3

# --- PAGE CONFIG ---
st.set_page_config(page_title="🧠 Focus Visualizer+", layout="wide")

# --- INIT STATES ---
if "focus_history" not in st.session_state:
    st.session_state.focus_history = []
if "target" not in st.session_state:
    st.session_state.target = random.randint(40, 80)
if "timer_active" not in st.session_state:
    st.session_state.timer_active = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "state_mode" not in st.session_state:
    st.session_state.state_mode = "random"

# --- EEG STATE FUNCTION ---
def generate_eeg_focus_state(state="random"):
    if state == "focus":
        return {"Delta (0.5–4 Hz) 🛌": 10, "Theta (4–8 Hz) 💭": 15, "Alpha (8–12 Hz) 🌙": 20, "Beta (12–30 Hz) 🔍": 70, "Gamma (30+ Hz) ⚡": 30}
    elif state == "relaxed":
        return {"Delta (0.5–4 Hz) 🛌": 30, "Theta (4–8 Hz) 💭": 45, "Alpha (8–12 Hz) 🌙": 60, "Beta (12–30 Hz) 🔍": 15, "Gamma (30+ Hz) ⚡": 5}
    elif state == "distracted":
        return {"Delta (0.5–4 Hz) 🛌": 25, "Theta (4–8 Hz) 💭": 50, "Alpha (8–12 Hz) 🌙": 10, "Beta (12–30 Hz) 🔍": 10, "Gamma (30+ Hz) ⚡": 2}
    else:
        return {
            "Delta (0.5–4 Hz) 🛌": np.random.normal(30, 5),
            "Theta (4–8 Hz) 💭": np.random.normal(20, 5),
            "Alpha (8–12 Hz) 🌙": np.random.normal(40, 5),
            "Beta (12–30 Hz) 🔍": np.random.normal(60, 5),
            "Gamma (30+ Hz) ⚡": np.random.normal(10, 5)
        }

# --- PDF EXPORT FUNCTION ---
def export_pdf(name, focus_level, zone, reflection):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Focus Visualizer+ Session Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Focus Level: {focus_level}", ln=True)
    pdf.cell(200, 10, txt=f"Zone: {zone}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Reflection:\n{reflection if reflection else 'No entry.'}")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- VOICE FEEDBACK ---
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    except:
        st.warning("Voice feedback unavailable on this device.")

# --- UI ---
st.title("🧠 Focus Visualizer+ (BCI-Inspired)")
st.write("A brain-simulated tool to explore focus, mood, and mini-BCI concepts 💫")

tab1, tab2, tab3 = st.tabs(["🎛️ Dashboard", "📂 EEG Upload", "📚 Learn Mode"])

with tab1:
    name = st.text_input("What's your name?")
    if name:
        st.markdown(f"Hi **{name}**! Let's check your focus today. 🌿")

    focus_level = st.slider("🎚️ Simulated Focus Level", 0, 100, 50)

    quotes = {
        "low": "Even clouds need rest ☁️ Take a breather.",
        "mid": "You're doing great 🌿 Keep the momentum going!",
        "high": "You're in the zone! 🚀 Stay with it!"
    }

    if focus_level < 30:
        zone = "low"
        st.markdown(f"### 😴 Low Focus ({focus_level})")
    elif 30 <= focus_level < 70:
        zone = "mid"
        st.markdown(f"### 😐 Moderate Focus ({focus_level})")
    else:
        zone = "high"
        st.markdown(f"### 🔥 High Focus ({focus_level})")

    st.info(quotes[zone])
    st.progress(focus_level / 100)

    st.session_state.state_mode = st.selectbox("🧠 Choose a Mental State to Simulate:", ["random", "focus", "relaxed", "distracted"])
    eeg_bands = generate_eeg_focus_state(st.session_state.state_mode)
    st.subheader("📊 EEG Frequency Bands")
    st.bar_chart(pd.Series(eeg_bands))

    st.subheader("🧍 Focus Avatar")
    st.markdown(
        ":smile:" if zone == "high" else ":neutral_face:" if zone == "mid" else ":sleeping:"
    )

    st.subheader("🖱️ Mind-Controlled Cursor Zone")
    col1, col2, col3 = st.columns(3)
    if focus_level < 33:
        col1.markdown("👁️‍🗨️")
    elif focus_level < 66:
        col2.markdown("👁️‍🗨️")
    else:
        col3.markdown("👁️‍🗨️")

    if st.button("📣 Speak This Zone"):
        speak(f"Your current zone is {zone} focus. {quotes[zone]}")

    if st.button("📈 Record Focus"):
        st.session_state.focus_history.append(focus_level)

    if st.session_state.focus_history:
        st.subheader("📊 Focus Over Time")
        st.line_chart(st.session_state.focus_history)

    with st.expander("🧪 Simulated EEG Signal (Noise-Based)"):
        fake_signal = np.random.normal(loc=focus_level, scale=10, size=20)
        st.line_chart(fake_signal)

    st.markdown("### 📝 Reflection Journal")
    reflection = st.text_area("How are you feeling right now?", placeholder="Write freely...")

    if st.button("💾 Save Session to CSV"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "Time": [timestamp],
            "Name": [name if name else "Anonymous"],
            "Focus Level": [focus_level],
            "Zone": [zone],
            "Reflection": [reflection]
        }
        df = pd.DataFrame(data)
        df.to_csv("focus_session.csv", index=False)
        st.success("✅ Session saved to `focus_session.csv`!")

    if st.button("🖨️ Export as PDF"):
        pdf_file = export_pdf(name if name else "Anonymous", focus_level, zone, reflection)
        st.download_button("📥 Download PDF Report", pdf_file, file_name="focus_report.pdf")

with tab2:
    st.subheader("📂 Upload EEG Data")
    uploaded = st.file_uploader("Upload your EEG CSV (with 'focus' column):", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.write("### Uploaded Data Preview")
        st.dataframe(df.head())
        if "focus" in df.columns:
            st.line_chart(df["focus"])
        else:
            st.error("No 'focus' column found in uploaded file.")

with tab3:
    st.subheader("📚 Learn About BCI")
    with st.expander("🧠 What are Brain Waves?"):
        st.write("Brainwaves are patterns of neural activity measured by EEG.")
    with st.expander("⚙️ Invasive vs Non-Invasive BCIs"):
        st.write("Invasive BCIs use implanted electrodes. Non-invasive use headbands or caps.")
    with st.expander("📺 Watch & Explore"):
        st.markdown("- [What is BCI? (YouTube)](https://youtu.be/ogBX18maUiM)")
        st.markdown("- [OpenBCI Website](https://openbci.com)")
        st.markdown("- [Muse Headband](https://choosemuse.com)")
    st.caption("This app simulates a basic BCI feedback loop. Replace data with real EEG in future!")
