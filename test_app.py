import streamlit as st
import sys
import os

# Set Keras compatibility BEFORE any other imports
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

st.title("🔧 Test Streamlit Cloud")
st.write("✅ Aplikacja działa!")
st.write(f"🐍 Python version: {sys.version}")

# Test TensorFlow
try:
    import tensorflow as tf
    st.write(f"🤖 TensorFlow version: {tf.__version__}")
    
    # Check Keras version
    try:
        import keras
        st.write(f"🔧 Keras version: {keras.__version__}")
        
        # Test LocallyConnected2D availability
        from tensorflow.keras.layers import LocallyConnected2D
        st.write("✅ LocallyConnected2D available")
    except ImportError as e:
        st.warning(f"⚠️ Keras layer import issue: {e}")
        
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
    
    st.write("🔄 Attempting to import DeepFace...")
    from deepface import DeepFace
    st.write("✅ DeepFace imported successfully")
    
    # Test DeepFace basic functionality with error handling
    try:
        st.write("🔄 Loading emotion model...")
        # Use a simpler backend first
        model = DeepFace.build_model("Emotion")
        st.write("✅ DeepFace emotion model loaded successfully")
    except Exception as model_error:
        st.warning(f"⚠️ Model loading issue: {model_error}")
        
except ImportError as import_error:
    st.error(f"❌ DeepFace import error: {import_error}")
    st.info("💡 This is likely due to Keras 3 compatibility issues")
except Exception as e:
    st.error(f"❌ DeepFace error: {e}")
    
# Show environment variables
st.subheader("🔧 Environment variables")
display_vars = ['QT_QPA_PLATFORM', 'DISPLAY', 'OPENCV_VIDEOIO_PRIORITY_MSMF']
for var in display_vars:
    value = os.environ.get(var, 'Not set')
    st.write(f"**{var}:** {value}")