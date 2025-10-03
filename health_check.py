#!/usr/bin/env python3
"""
Health check script for Streamlit Cloud deployment
"""
import sys
import os

# Set environment variables for stability
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['PYTHONHASHSEED'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def check_imports():
    """Check if all required imports work"""
    try:
        print("Checking imports...")
        import streamlit
        print("✅ Streamlit OK")
        
        import cv2
        print("✅ OpenCV OK")
        
        import numpy
        print("✅ NumPy OK")
        
        import matplotlib
        print("✅ Matplotlib OK")
        
        import tensorflow
        print("✅ TensorFlow OK")
        
        from deepface import DeepFace
        print("✅ DeepFace OK")
        
        # Optional imports
        try:
            from streamlit_webrtc import webrtc_streamer
            print("✅ Streamlit-WebRTC OK (camera functionality available)")
        except ImportError:
            print("⚠️ Streamlit-WebRTC not available (camera functionality disabled)")
        
        print("✅ All core imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    if check_imports():
        print("🎉 Health check passed!")
        sys.exit(0)
    else:
        print("💥 Health check failed!")
        sys.exit(1)