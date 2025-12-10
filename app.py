import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️", layout="wide")

# --- YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=100)
    st.title("PhishGuard AI")
    st.markdown("Kurumsal E-posta Güvenlik Analisti")

    # API Key Yönetimi (Güvenlik İçin)
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key

    st.divider()
    st.info("Bu sistem RAG (Retrieval-Augmented Generation) teknolojisi kullanır.")

# --- ANA EKRAN ---
st.header("🛡️ E-posta Güvenlik Analizi")
st.write("Şüpheli e-postayı aşağıya yapıştırın, yapay zeka şirket kurallarına göre analiz etsin.")

email_input = st.text_area("E-posta İçeriği:", height=200, placeholder="From: CEO\nSubject: Urgent...")

if st.button("ANALİZ ET 🚀", type="primary"):
    if not api_key:
        st.error("Lütfen sol menüden API Key giriniz!")
        st.stop()

    if not email_input:
        st.warning("Lütfen bir e-posta metni girin.")
        st.stop()

    with st.spinner("Veritabanı taranıyor ve analiz yapılıyor..."):
        try:
            # 1. RAG SİSTEMİNİ YÜKLE
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vector_store = FAISS.load_local("sirket_vektor_db", embeddings, allow_dangerous_deserialization=True)

            # 2. KURALLARI GETİR
            docs = vector_store.similarity_search(email_input, k=2)
            context_text = "\n".join([d.page_content for d in docs])

            # 3. LLM'İ HAZIRLA
            llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

            system_prompt = """
            You are a Senior Cyber Security Analyst.
            Use the following COMPANY RULES (Context) to analyze the email.

            CONTEXT:
            {context}

            INSTRUCTIONS:
            1. First check if it violates specific COMPANY RULES. Cite them.
            2. Then check for general phishing indicators.
            3. Reply in clear Markdown format.
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "<email>\n{email_icerigi}\n</email>")
            ])

            # 4. ÇALIŞTIR
            chain = prompt | llm
            sonuc = chain.invoke({"context": context_text, "email_icerigi": email_input})

            # 5. SONUCU GÖSTER
            st.success("Analiz Tamamlandı!")

            # İki sütuna bölelim: Sol taraf Analiz, Sağ taraf Bulunan Kurallar
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("📝 Yapay Zeka Raporu")
                st.markdown(sonuc.content)

            with col2:
                st.subheader("📚 Referans Kurallar")
                st.info(context_text)

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            st.warning("İpucu: 'rag_setup.py' dosyasını çalıştırıp veritabanını oluşturdunuz mu?")