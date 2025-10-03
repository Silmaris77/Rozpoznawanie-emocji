import streamlit as st
import sys

st.title("🔧 Test Streamlit Cloud")
st.write("✅ Aplikacja działa!")
st.write(f"🐍 Python version: {sys.version}")

try:
    import tensorflow as tf
    st.write(f"🤖 TensorFlow version: {tf.__version__}")
except Exception as e:
    st.error(f"❌ TensorFlow error: {e}")

try:
    from deepface import DeepFace
    st.write("✅ DeepFace imported successfully")
except Exception as e:
    st.error(f"❌ DeepFace error: {e}")

try:
    import cv2
    st.write(f"👁️ OpenCV version: {cv2.__version__}")
except Exception as e:
    st.error(f"❌ OpenCV error: {e}")