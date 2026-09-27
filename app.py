import streamlit as st
from google import genai
from PIL import Image
import streamlit.components.v1 as components

# Sayfa Yapılandırması
st.set_page_config(page_title="Yapay Zeka Özel Öğretmenim", page_icon="🎓", layout="centered")

# Menü ve başlık gizleme (Profesyonel Görünüm)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 Yapay Zeka Özel Öğretmenim")
st.write("Matematik, Fizik, Kimya, Biyoloji, Türkçe, Tarih... İstediğin her dersi yazabilir veya sorunun **fotoğrafını yükleyebilirsin!**")

# API Key'i Streamlit Secrets'tan al
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else None

if not api_key:
    api_key = st.sidebar.text_input("Google Gemini API Key Giriniz:", type="password")
    if not api_key:
        st.info("Lütfen API Key giriniz veya Streamlit Secrets alanına ekleyiniz.")
        st.stop()

# GenAI İstemcisini Başlat
client = genai.Client(api_key=api_key)

# Genel Evrensel Öğretmen Talimatı
teacher_instruction = (
    "Sen her branşta uzman, son derece sabırlı, cesaretlendirici ve Sokratik yöntem kullanan evrensel bir özel öğretmensin. "
    "Öğrenci sana metin olarak veya soru fotoğrafı yükleyerek ne sorarsa sorsun, sorunun hangi derse ait olduğunu tespit et ve o branşın uzman öğretmeni üslubuyla yanıt ver. "
    "Fotoğraftaki soruyu dikkatlice analiz et, metinleri ve şekilleri tam oku. "
    "Doğrudan tek kelimelik cevabı verip geçmek yerine öğrenciye konunun mantığını kavratacak şekilde adım adım rehberlik et."
)

# Seslendirme HTML/JavaScript Bileşeni Fonksiyonu
def play_audio_script(text):
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    html_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance('{clean_text}');
    msg.lang = 'tr-TR';
    msg.rate = 1.0;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(html_code, height=0, width=0)

# Sohbet Geçmişi Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş Mesajları Ekrana Yazdırma
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Fotoğraf Yükleme Alanı
uploaded_file = st.file_uploader("📸 Soru Fotoğrafı Yükle (İsteğe Bağlı):", type=["jpg", "jpeg", "png"])

# Kullanıcı Soru Girişi (Chat Input)
if prompt := st.chat_input("İstediğin dersten sorunu yaz veya fotoğraf yükleyip gönder..."):
    
    # Fotoğraf yüklendi mi kontrolü
    image_obj = None
    if uploaded_file is not None:
        image_obj = Image.open(uploaded_file)
        
    # Kullanıcı mesajını ekrana ve geçmişe ekle
    if image_obj:
        st.session_state.messages.append({"role": "user", "content": f"📸 [Fotoğraf Yüklendi]\n\n{prompt}"})
        with st.chat_message("user"):
            st.image(image_obj, caption="Yüklenen Soru Fotoğrafı", use_container_width=True)
            st.markdown(prompt)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Yapay Zeka Yanıtı (Canlı Akış / Streaming)
    with st.chat_message("assistant"):
        def generate_response():
            # Google API'nin resmi olarak önerdiği model isimleri
            models_to_try = ['gemini-3.8-flash', 'models/gemini-3.8-flash']
            
            # İçerik hazırlığı
            contents_payload = [teacher_instruction, prompt]
            if image_obj:
                contents_payload.append(image_obj)
            
            last_error = None
            for model_name in models_to_try:
                try:
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=contents_payload
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                    return
                except Exception as e:
                    last_error = e
                    continue
            
            yield f"\n\n*Hata oluştu: {last_error}*"

        full_response = st.write_stream(generate_response)
        
        # Yanıt başarıyla alındıysa seslendir
        if full_response and not full_response.startswith("\n\n*Hata oluştu:"):
            play_audio_script(full_response)
    
    # Yanıtı geçmişe ekle
    st.session_state.messages.append({"role": "assistant", "content": full_response})
