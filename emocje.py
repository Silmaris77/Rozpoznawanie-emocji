import os
import sys

# Import Streamlit first to avoid conflicts
try:
    import streamlit as st
    st.write("🚀 Starting Emotion Recognition App...")
    st.write("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Streamlit: {e}")
    sys.exit(1)

# Set environment variables before any imports to handle Keras compatibility
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['PYTHONHASHSEED'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU usage to avoid GPU memory issues

# Memory management for stability
import gc
gc.set_threshold(700, 10, 10)

# Add error handling for imports
print("🔄 Starting application...")
print(f"Python version: {sys.version}")

try:
    print("🤖 Importing DeepFace...")
    from deepface import DeepFace
    print("✅ DeepFace imported successfully")
    
    print("📊 Importing matplotlib...")
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')  # Use non-interactive backend for stability
    print("✅ matplotlib imported successfully")
    
    print("👁️ Importing OpenCV...")
    import cv2
    print("✅ OpenCV imported successfully")
    
    print("🔢 Importing numpy...")
    import numpy as np
    print("✅ numpy imported successfully")
    import tempfile
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.patches as patches
    
    # Import with type stubs for optional webrtc
    try:
        from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration  # type: ignore
        import av
        WEBRTC_AVAILABLE = True
        
        # Define the real VideoProcessor when webrtc is available
        class VideoProcessor(VideoTransformerBase):  # type: ignore
            """Klasa do przetwarzania wideo z kamery w czasie rzeczywistym"""
            
            def __init__(self):
                self.frame_count = 0
                self.analyze_every_n_frames = 30  # Analizuj co 30 klatek (około sekundy przy 30 FPS)
            
            def recv(self, frame):
                global latest_emotion_result, emotion_lock
                
                img = frame.to_ndarray(format="bgr24")
                
                # Analizuj emocje co N klatek żeby nie obciążać procesora
                if self.frame_count % self.analyze_every_n_frames == 0:
                    try:
                        # Zapisz klatkę tymczasowo
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                            cv2.imwrite(tmp_file.name, img)
                            
                            # Analizuj emocje (szybko, bez enforce_detection) with error handling
                            try:
                                result = DeepFace.analyze(
                                    tmp_file.name, 
                                    actions=['emotion'], 
                                    enforce_detection=False,
                                    silent=True,
                                    detector_backend='opencv'  # Use stable backend
                                )
                                
                                # Zapisz wynik
                                with emotion_lock:
                                    if isinstance(result, list):
                                        latest_emotion_result = result[0]
                                    else:
                                        latest_emotion_result = result
                            except Exception:
                                # Silently handle analysis errors in real-time mode
                                pass
                            
                            # Usuń plik tymczasowy
                            os.unlink(tmp_file.name)
                            
                    except Exception as e:
                        pass  # Zignoruj błędy analizy
                
                # Jeśli mamy wynik analizy, narysuj na obrazie
                with emotion_lock:
                    if latest_emotion_result is not None:
                        try:
                            emotions = latest_emotion_result.get('emotion', {})  # type: ignore
                            face_region = latest_emotion_result.get('region', {})  # type: ignore
                            
                            if emotions and face_region:
                                # Znajdź dominującą emocję
                                dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                                
                                # Narysuj prostokąt wokół twarzy
                                x, y, w, h = face_region.get('x', 0), face_region.get('y', 0), face_region.get('w', 0), face_region.get('h', 0)
                                if x > 0 and y > 0 and w > 0 and h > 0:
                                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                    
                                    # Dodaj tekst z emocją
                                    emotion_emoji = {
                                        'happy': '😊', 'sad': '😢', 'angry': '😠', 'surprise': '😮', 
                                        'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
                                    }
                                    emoji = emotion_emoji.get(dominant_emotion[0], '🎭')
                                    label = f"{dominant_emotion[0]}: {dominant_emotion[1]:.1f}%"  # Usunąłem emoji bo może nie działać w OpenCV
                                    
                                    # Rysuj tło dla tekstu
                                    font = cv2.FONT_HERSHEY_SIMPLEX
                                    font_scale = 0.6
                                    thickness = 2
                                    (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
                                    
                                    cv2.rectangle(img, (x, y - text_height - 10), (x + text_width, y), (0, 255, 0), -1)
                                    cv2.putText(img, label, (x, y - 5), font, font_scale, (0, 0, 0), thickness)
                            
                        except Exception as e:
                            pass  # Zignoruj błędy rysowania
                
                self.frame_count += 1
                return av.VideoFrame.from_ndarray(img, format="bgr24")
        
    except ImportError:
        WEBRTC_AVAILABLE = False
        st.warning("⚠️ Camera functionality is not available. Only file upload mode will work.")
        
        # Define dummy classes when webrtc is not available
        class VideoTransformerBase:
            pass
            
        class VideoProcessor:
            def __init__(self):
                self.frame_count = 0
                self.analyze_every_n_frames = 30
                
        class RTCConfiguration:
            def __init__(self, *args, **kwargs):
                pass
                
        def webrtc_streamer(*args, **kwargs):
            return None
    
    import threading
    import time
    from typing import Optional, Dict, Any, Tuple
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Memory management functions
def cleanup_memory():
    """Clean up memory to prevent segmentation faults"""
    gc.collect()
    plt.close('all')

@st.cache_data(show_spinner=False)
def load_deepface_model():
    """Preload DeepFace model with caching"""
    try:
        # Trigger model loading with a dummy analysis
        import numpy as np
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            cv2.imwrite(tmp_file.name, dummy_img)
            try:
                DeepFace.analyze(tmp_file.name, actions=['emotion'], enforce_detection=False, silent=True)
            except:
                pass
            finally:
                os.unlink(tmp_file.name)
        return True
    except Exception:
        return False

# Konfiguracja strony
st.set_page_config(
    page_title="🎭 Analizator Emocji AI",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylizacja CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
        border-left: 4px solid #ff7f0e;
        padding-left: 1rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .emotion-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .sidebar-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .uploadedFile {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def draw_emotion_on_face(image_path: str, face_region: Dict[str, int], dominant_emotion: str, confidence: float) -> Optional[np.ndarray]:
    """Rysuje prostokąt wokół twarzy i oznacza emocję"""
    # Wczytaj obraz
    img = cv2.imread(image_path)
    if img is None:
        return None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Pobierz współrzędne twarzy
    x, y, w, h = face_region['x'], face_region['y'], face_region['w'], face_region['h']
    
    # Narysuj prostokąt wokół twarzy
    cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 255, 0), 3)
    
    # Dodaj tekst z emocją
    label = f"{dominant_emotion}: {confidence:.1f}%"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    
    # Oblicz rozmiar tekstu
    (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
    
    # Narysuj tło dla tekstu
    cv2.rectangle(img_rgb, (x, y - text_height - 10), (x + text_width, y), (0, 255, 0), -1)
    
    # Narysuj tekst
    cv2.putText(img_rgb, label, (x, y - 5), font, font_scale, (0, 0, 0), thickness)
    
    return img_rgb

def create_face_analysis_plot(image_path: str, result: Any) -> Tuple[Optional[np.ndarray], Optional[Dict[str, float]], Optional[Tuple[str, float]]]:
    """Tworzy wykres z zaznaczoną twarzą i emocjami"""
    # Wczytaj obraz
    img = cv2.imread(image_path)
    if img is None:
        return None, None, None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Przygotuj dane
    if isinstance(result, list):
        face_data = result[0]
    else:
        face_data = result
    
    emotions = face_data['emotion']
    face_region = face_data['region']
    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
    
    # Narysuj obraz z oznaczoną twarzą
    annotated_img = draw_emotion_on_face(image_path, face_region, dominant_emotion[0], dominant_emotion[1])
    
    return annotated_img, emotions, dominant_emotion

# Globalne zmienne dla kamery
latest_emotion_result = None
emotion_lock = threading.Lock()

# Główny nagłówek aplikacji
st.markdown('<h1 class="main-header">🎭 Analizator Emocji AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Wykrywaj emocje na zdjęciach dzięki sztucznej inteligencji</p>', unsafe_allow_html=True)

# === SIDEBAR ===
st.sidebar.markdown("## �️ Panel Kontrolny")

# Informacje o aplikacji
with st.sidebar.expander("ℹ️ O Aplikacji", expanded=True):
    st.markdown("""
    **�🎭 Analizator Emocji AI** używa zaawansowanych algorytmów deep learning do:
    
    • 🔍 Wykrywania twarzy na zdjęciach
    • 🎯 Analizy wyrazu emocjonalnego
    • 📊 Generowania szczegółowych raportów
    • 🎨 Wizualizacji wyników
    """)

# Ustawienia analizy
st.sidebar.markdown("### ⚙️ Ustawienia Analizy")

# Wybór źródła obrazu
if WEBRTC_AVAILABLE:
    source_options = ["📸 Przesyłanie pliku", "📹 Kamera internetowa"]
else:
    source_options = ["📸 Przesyłanie pliku"]
    
source_option = st.sidebar.radio(
    "📹 Źródło obrazu:",
    source_options,
    help="Wybierz skąd chcesz analizować emocje"
)

confidence_threshold = st.sidebar.slider(
    "🎯 Próg pewności (%)", 
    min_value=0, 
    max_value=100, 
    value=50,
    help="Minimalny poziom pewności dla wykrywania twarzy"
)

show_advanced = st.sidebar.checkbox("🔬 Pokaż zaawansowane opcje", False)

if show_advanced:
    detection_backend = st.sidebar.selectbox(
        "🔍 Backend wykrywania",
        ["opencv", "retinaface", "mtcnn"],
        index=0,
        help="Wybierz algorytm wykrywania twarzy"
    )
    
    model_name = st.sidebar.selectbox(
        "🧠 Model analizy",
        ["VGG-Face", "Facenet", "OpenFace", "DeepFace"],
        index=0,
        help="Wybierz model do analizy emocji"
    )
else:
    detection_backend = "opencv"
    model_name = "VGG-Face"

# Statystyki
st.sidebar.markdown("### 📈 Statystyki")
with st.sidebar.container():
    st.markdown("""
    <div class="metric-container">
        <h4>🎯 Emocje do wykrycia:</h4>
        <p>😊 Radość • 😢 Smutek • 😠 Złość<br>
        😮 Zdziwienie • 😨 Strach • 🤢 Obrzydzenie<br>
        😐 Neutralność</p>
    </div>
    """, unsafe_allow_html=True)

# Pomoc
with st.sidebar.expander("💡 Wskazówki"):
    st.markdown("""
    **📸 Najlepsze rezultaty osiągniesz gdy:**
    
    ✅ Twarz jest dobrze oświetlona  
    ✅ Osoba patrzy w kierunku kamery  
    ✅ Zdjęcie jest ostre i wyraźne  
    ✅ Twarz zajmuje większą część kadru  
    
    **❌ Unikaj:**
    
    ❌ Zdjęć zbyt ciemnych lub jasnych  
    ❌ Twarzy zakrytych lub w profilu  
    ❌ Zdjęć rozmytych lub pixelowanych  
    """)

# === GŁÓWNA ZAWARTOŚĆ ===

if source_option == "📸 Przesyłanie pliku":
    # Sekcja upload-u zdjęcia
    st.markdown('<div class="sub-header">📸 Prześlij Zdjęcie do Analizy</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "",
            type=["jpg", "jpeg", "png", "bmp", "tiff"],
            help="Wybierz zdjęcie z wyraźnie widoczną twarzą",
            label_visibility="collapsed"
        )
        
        if uploaded_file is None:
            st.markdown("""
            <div class="uploadedFile">
                <h3>📸 Przeciągnij i upuść zdjęcie tutaj</h3>
                <p>lub kliknij aby wybrać plik</p>
                <p><small>Obsługiwane formaty: JPG, PNG, BMP, TIFF</small></p>
            </div>
            """, unsafe_allow_html=True)

else:  # Kamera internetowa
    if WEBRTC_AVAILABLE:
        st.markdown('<div class="sub-header">📹 Kamera Internetowa - Analiza Real-time</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="emotion-card">
            <h4>🎥 Analiza emocji w czasie rzeczywistym</h4>
            <p>• Kamera analizuje Twoje emocje na żywo</p>
            <p>• Wyniki są aktualizowane co około sekundę</p>
            <p>• Zielony prostokąt pokazuje wykrytą twarz</p>
            <p>• Nazwa emocji pojawia się nad twarzą</p>
        </div>
        """, unsafe_allow_html=True)
        
        if WEBRTC_AVAILABLE:
            # Konfiguracja WebRTC
            RTC_CONFIGURATION = RTCConfiguration({
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            })
            
            # Stream z kamery z analizą emocji
            webrtc_ctx = webrtc_streamer(
                key="emotion-analysis",
                video_processor_factory=VideoProcessor,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )
            
            # Wyświetlaj bieżące wyniki analizy
            if webrtc_ctx and webrtc_ctx.video_processor:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Bieżąca Analiza")
                    emotion_placeholder = st.empty()
                    
                with col2:
                    st.markdown("#### 🎯 Statystyki")
                    stats_placeholder = st.empty()
                
                # Aktualizuj wyniki w czasie rzeczywistym
                if hasattr(webrtc_ctx, 'state') and webrtc_ctx.state.playing:
                    with emotion_lock:
                        if latest_emotion_result is not None:
                            try:
                                emotions = latest_emotion_result.get('emotion', {})  # type: ignore
                                if emotions:
                                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
                                    
                                    # Emoji dla emocji
                                    emotion_emoji = {
                                        'happy': '😊', 'sad': '😢', 'angry': '😠', 'surprise': '😮', 
                                        'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
                                    }
                                    emoji = emotion_emoji.get(dominant_emotion[0], '🎭')
                                    
                                    # Aktualizuj wyświetlanie
                                    with emotion_placeholder.container():
                                        st.markdown(f"""
                                        <div class="emotion-card">
                                            <h2>{emoji} {dominant_emotion[0].upper()}</h2>
                                            <h3>Pewność: {dominant_emotion[1]:.1f}%</h3>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # Wyświetl wszystkie emocje
                                    with stats_placeholder.container():
                                        for emotion, value in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]:
                                            emoji_e = emotion_emoji.get(emotion, '🎭')
                                            st.write(f"{emoji_e} {emotion}: {value:.1f}%")
                            except Exception:
                                pass
                    
                    time.sleep(0.5)  # Aktualizuj co pół sekundy
        else:
            st.error("⚠️ Funkcjonalność kamery nie jest dostępna w tym środowisku.")
            st.info("🔄 Użyj opcji 'Przesyłanie pliku' aby analizować emocje ze zdjęć.")
    
    uploaded_file = None  # Brak pliku dla kamery

if uploaded_file is not None:
    # Zapisz plik tymczasowo, bo DeepFace wymaga ścieżki do pliku
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    
    # Sekcja wyświetlania zdjęć
    st.markdown('<div class="sub-header">🖼️ Przesłane Zdjęcie</div>', unsafe_allow_html=True)
    
    # Wyświetl oryginalne zdjęcie w eleganckiej ramce
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(uploaded_file, caption="📷 Oryginalne zdjęcie", use_container_width=True)
    
    # Rozpocznij analizę
    st.markdown('<div class="sub-header">🤖 Analiza AI w Toku</div>', unsafe_allow_html=True)
    
    try:
        # Preload model if not already loaded
        load_deepface_model()
        
        # Clean memory before analysis
        cleanup_memory()
        
        # Analiza emocji używając DeepFace with better error handling
        with st.spinner('🔍 Analizuję emocje i wykrywam twarz... To może potrwać chwilę.'):
            try:
                result = DeepFace.analyze(
                    tmp_path, 
                    actions=['emotion'], 
                    enforce_detection=False,
                    silent=True,
                    detector_backend='opencv'  # Use more stable backend
                )
            except Exception as analysis_error:
                st.error(f"Błąd podczas analizy obrazu: {str(analysis_error)}")
                st.info("Spróbuj użyć innego zdjęcia lub sprawdź czy twarz jest wyraźnie widoczna.")
                raise analysis_error
        
        # Clean memory after analysis
        cleanup_memory()
        
        # Utwórz wizualizację z zaznaczoną twarzą
        annotated_img, emotions, dominant_emotion = create_face_analysis_plot(tmp_path, result)
        
        if annotated_img is not None and emotions is not None and dominant_emotion is not None:
            # Sekcja wyników
            st.markdown('<div class="sub-header">🎯 Wyniki Analizy</div>', unsafe_allow_html=True)
            
            # Wyświetl obraz z zaznaczoną twarzą i emocją
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(annotated_img, caption=f"🎭 Wykryta emocja: {dominant_emotion[0]} ({dominant_emotion[1]:.1f}%)", 
                        use_container_width=True)
            
            # Pokaż dominującą emocję w eleganckiej karcie
            emotion_emoji = {
                'happy': '😊', 'sad': '😢', 'angry': '😠', 'surprise': '😮', 
                'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
            }
            emotion_colors = {
                'happy': '#28a745', 'sad': '#6f42c1', 'angry': '#dc3545', 'surprise': '#ffc107', 
                'fear': '#6c757d', 'disgust': '#20c997', 'neutral': '#17a2b8'
            }
            
            emoji = emotion_emoji.get(dominant_emotion[0], '🎭')
            color = emotion_colors.get(dominant_emotion[0], '#17a2b8')
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}22, {color}44); 
                        border-left: 4px solid {color}; 
                        padding: 1.5rem; 
                        border-radius: 10px; 
                        margin: 1rem 0;
                        text-align: center;">
                <h2>{emoji} Dominująca Emocja: {dominant_emotion[0].upper()}</h2>
                <h3>Pewność: {dominant_emotion[1]:.1f}%</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Sekcja wykresów i szczegółowych analiz
        st.markdown('<div class="sub-header">📊 Szczegółowa Analiza Emocji</div>', unsafe_allow_html=True)
        
        # Utwórz dwie kolumny dla wykresów
        col1, col2 = st.columns(2)
        
        with col1:
            # Wykres słupkowy emocji
            st.markdown("#### 📊 Wykres słupkowy")
            if emotions is not None:
                fig, ax = plt.subplots(figsize=(8, 6))
                
                # Kolorowe słupki dla każdej emocji
                emotion_colors_plot = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#95e1d3']
                bars = ax.bar(list(emotions.keys()), list(emotions.values()), color=emotion_colors_plot[:len(emotions)])
                ax.set_ylabel('Pewność (%)', fontsize=12)
                ax.set_title('Rozkład wszystkich emocji', fontsize=14, pad=20)
                ax.set_ylim(0, 100)
                
                # Dodaj wartości na słupkach
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
                
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
        
        with col2:
            # Wykres kołowy emocji
            st.markdown("#### 🥧 Wykres kołowy")
            if emotions is not None:
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#95e1d3']
                
                # Filtruj tylko emocje > 1% dla czytelności
                filtered_emotions = {k: v for k, v in emotions.items() if v > 1}
                if not filtered_emotions:  # Jeśli wszystkie są < 1%, pokaż wszystkie
                    filtered_emotions = emotions
                
                pie_result = ax2.pie(
                    list(filtered_emotions.values()), 
                    labels=list(filtered_emotions.keys()), 
                    autopct='%1.1f%%', 
                    colors=colors[:len(filtered_emotions)], 
                    startangle=90,
                    textprops={'fontsize': 10}
                )
                # Handle variable unpacking based on return type
                if len(pie_result) == 3:
                    wedges, texts, autotexts = pie_result
                else:
                    wedges, texts = pie_result
                    autotexts = []
                ax2.set_title('Procentowy rozkład emocji', fontsize=14, pad=20)
                st.pyplot(fig2)
        
        # Szczegółowa tabela wyników
        if emotions is not None:
            st.markdown('<div class="sub-header">📋 Ranking Emocji</div>', unsafe_allow_html=True)
            
            # Przygotuj dane do tabeli
            emotion_data = []
            for i, (emotion, value) in enumerate(sorted(emotions.items(), key=lambda x: x[1], reverse=True), 1):
                emoji_map = {
                    'happy': '😊', 'sad': '😢', 'angry': '😠', 'surprise': '😮', 
                    'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
                }
                color_map = {
                    'happy': '🟢', 'sad': '🔵', 'angry': '🔴', 'surprise': '🟡', 
                    'fear': '⚫', 'disgust': '🟢', 'neutral': '⚪'
                }
                
                emotion_data.append({
                    "Pozycja": f"{i}.",
                    "Emocja": f"{emoji_map.get(emotion, '🎭')} {emotion.title()}",
                    "Pewność": f"{value:.2f}%",
                    "Status": color_map.get(emotion, '⚪')
                })
            
            # Wyświetl tabelę w 3 kolumnach
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                for item in emotion_data:
                    confidence = float(item["Pewność"].replace('%', ''))
                    if confidence > 50:
                        status_color = "🔥 Wysoka"
                    elif confidence > 20:
                        status_color = "🔶 Średnia"
                    else:
                        status_color = "🔹 Niska"
                    
                    st.markdown(f"""
                    <div class="emotion-card">
                        <strong>{item['Pozycja']} {item['Emocja']}</strong><br>
                        <span style="font-size: 1.2em; color: #1f77b4;">{item['Pewność']}</span>
                        <span style="float: right;">{status_color}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.markdown('<div class="sub-header">❌ Problem z Analizą</div>', unsafe_allow_html=True)
            st.error("Nie udało się wykryć twarzy na zdjęciu.")
        
    except Exception as e:
        st.error(f"Błąd podczas analizy: {str(e)}")
        st.info("Spróbuj użyć innego zdjęcia z wyraźnie widoczną twarzą.")
    
    finally:
        # Usuń plik tymczasowy
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        # Clean up memory after processing
        cleanup_memory()
