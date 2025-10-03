import streamlit as st
import sys
import os

# Set environment variables for headless mode
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''

st.set_page_config(
    page_title="🎭 Rozpoznawanie Emocji",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 Analizator Emocji AI")
st.markdown("**Wykrywaj emocje na zdjęciach dzięki sztucznej inteligencji**")

# Check if we're in fallback mode
st.info("⚠️ Aplikacja działa w trybie uproszczonym")
st.info("📤 Możesz przesłać zdjęcie, ale analiza emocji jest tymczasowo niedostępna")

# File upload
uploaded_file = st.file_uploader(
    "📁 Wybierz zdjęcie do analizy",
    type=['png', 'jpg', 'jpeg'],
    help="Prześlij zdjęcie twarzy do analizy emocji"
)

if uploaded_file is not None:
    # Display the image
    st.image(uploaded_file, caption="Przesłane zdjęcie", use_column_width=True)
    
    st.warning("🔧 Analiza emocji jest tymczasowo niedostępna z powodu problemów z bibliotekami")
    st.info("💡 Pracujemy nad rozwiązaniem problemu. Spróbuj ponownie później.")
    
    # Show mock results for demonstration
    st.subheader("📊 Przykładowe wyniki analizy:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Dominująca emocja", "😊 Happy", "75%")
        
    with col2:
        # Mock emotion distribution
        emotions = {
            'Happy': 0.75,
            'Neutral': 0.15,
            'Surprise': 0.05,
            'Sad': 0.03,
            'Angry': 0.02
        }
        
        for emotion, score in emotions.items():
            st.progress(score, text=f"{emotion}: {score:.0%}")

st.markdown("---")
st.markdown("🔧 **Status techniczny:** Aplikacja działa w trybie fallback")
st.markdown(f"🐍 **Python:** {sys.version}")

# Technical info
with st.expander("ℹ️ Informacje techniczne"):
    st.write("Aplikacja jest tymczasowo uruchomiona bez pełnej funkcjonalności analizy emocji.")
    st.write("Główne problemy:")
    st.write("- Konflikt bibliotek OpenCV na serwerze")
    st.write("- Problemy z libGL.so.1 na headless systemie")
    st.write("- Oczekiwanie na rozwiązanie problemów zależności")