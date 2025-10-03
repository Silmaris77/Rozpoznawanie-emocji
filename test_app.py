import streamlit as st
import sys
import os

st.title("🔧 Test Streamlit Cloud")
st.write("✅ Aplikacja działa!")
st.write(f"🐍 Python version: {sys.version}")

# Test TensorFlow
try:
    import tensorflow as tf
    st.write(f"🤖 TensorFlow version: {tf.__version__}")
except Exception as e:
    st.error(f"❌ TensorFlow error: {e}")

# Test OpenCV headless first
try:
    # Force headless mode
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    import cv2
    st.write(f"👁️ OpenCV version: {cv2.__version__}")
    st.write("✅ OpenCV headless imported successfully")
    
    # Test basic OpenCV operation
    import numpy as np
    test_img = np.zeros((100, 100, 3), dtype=np.uint8)
    gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    st.write("✅ OpenCV basic operations working")
    
except Exception as e:
    st.error(f"❌ OpenCV error: {e}")

# Test DeepFace
try:
    # Set environment for headless operation
    os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
    
    from deepface import DeepFace
    st.write("✅ DeepFace imported successfully")
    
    # Test DeepFace basic functionality
    backends = DeepFace.build_model("Emotion")
    st.write("✅ DeepFace emotion model loaded successfully")
    
except Exception as e:
    st.error(f"❌ DeepFace error: {e}")
    
# Show environment variables
st.subheader("🔧 Environment variables")
display_vars = ['QT_QPA_PLATFORM', 'DISPLAY', 'OPENCV_VIDEOIO_PRIORITY_MSMF']
for var in display_vars:
    value = os.environ.get(var, 'Not set')
    st.write(f"**{var}:** {value}")