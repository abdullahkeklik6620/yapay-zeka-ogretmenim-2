import streamlit as st
from google import genai
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
st.write("Matematik, Fizik, Kimya, Biyoloji, Türkçe, Tarih... İstediğin her dersi doğrudan sorabilirsin!")

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
    "Öğrenci sana hangi dersten soru sorarsa sorsun (Matematik, Fizik, Kimya, Biyoloji, Türkçe, Edebiyat, Tarih, Coğrafya, İngilizce vb.), "
    "sorunun hangi derse ait olduğunu otomatik olarak tespit et ve o branşın uzman öğretmeni üslubuyla yanıt ver. "
    "Doğrudan cevabı verip geçmek yerine öğrenciye konunun mantığını kavratacak şekilde adım adım rehberlik et."
)

# Seslendirme HTML/JavaScript Bileşeni Fonksiyonu
def play_audio_script(text):
    # Özel karakterleri ve tırnak işaretlerini temizleme
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    html_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance('{clean_text}');
    msg.lang = 'tr-TR';
    msg.rate = 1.0;
    window.speechSynthesis.cancel(); // Önceki seslendirmeyi durdur
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

# Kullanıcı Soru Girişi (Chat Input)
if prompt := st.chat_input("İstediğin dersten sorunu yaz..."):
    # Kullanıcı mesajını ekrana ve geçmişe ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay Zeka Yanıtı (Canlı Akış / Streaming)
    with st.chat_message("assistant"):
        def generate_response():
            models_to_try = ['gemini-3.8-flash', 'gemini-2.5-flash']
            
            for model_name in models_to_try:
                try:
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=f"{teacher_instruction}\n\nÖğrencinin Sorusu: {prompt}"
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                    return
                except Exception as e:
                    continue
            
            yield "\n\n*Şu anda yapay zeka sunucularında yoğunluk var, lütfen birkaç saniye sonra tekrar deneyiniz.*"

        full_response = st.write_stream(generate_response)
        
        # Otomatik seslendirmeyi çalıştır
        if full_response:
            play_audio_script(full_response)
    
    # Yanıtı geçmişe ekle
    st.session_state.messages.append({"role": "assistant", "content": full_response})
