import streamlit as st
from google import genai

# Sayfa Yapılandırması
st.set_page_config(page_title="Yapay Zeka Özel Öğretmenim", page_icon="🎓", layout="centered")

st.title("🎓 Yapay Zeka Özel Öğretmenim")
st.write("Matematik, Fizik, Kimya, Biyoloji, Türkçe, Tarih... İstediğin her dersi doğrudan sorabilirsin!")

# Yan Menü: Sadece API Key
st.sidebar.header("⚙️ Ayarlar")
api_key = st.sidebar.text_input("Google Gemini API Key Giriniz:", type="password")

if not api_key:
    st.info("Lütfen sol menüden Google AI Studio'dan aldığınız API Key'i giriniz.")
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
            try:
                response_stream = client.models.generate_content_stream(
                    model='gemini-3.8-flash',
                    contents=f"{teacher_instruction}\n\nÖğrencinin Sorusu: {prompt}"
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                yield f"\n\n*Hata oluştu: {e}*"

        full_response = st.write_stream(generate_response)
    
    # Yanıtı geçmişe ekle
    st.session_state.messages.append({"role": "assistant", "content": full_response})