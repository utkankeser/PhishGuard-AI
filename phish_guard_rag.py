import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- 1. AYARLAR ---
api_key = "BURAYA_API_KEY_YAPISTIR"
os.environ["GROQ_API_KEY"] = api_key

# --- 2. HAFIZAYI YÜKLE (RAG) ---
print("Hafıza yükleniyor...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Daha önce kaydettiğimiz veritabanını diskten okuyoruz
try:
    vector_store = FAISS.load_local("sirket_vektor_db", embeddings, allow_dangerous_deserialization=True)
    print("✅ Şirket kuralları başarıyla yüklendi.")
except Exception as e:
    print("❌ Veritabanı bulunamadı! Önce rag_setup.py'yi çalıştırdın mı?")
    exit()

# --- 3. BEYİN (LLM) ---
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

# --- 4. GELİŞMİŞ PERSONA (Context Aware) ---
# Burası çok önemli: Modele "Context" (Bağlam) adında yeni bir bilgi alanı açıyoruz.
system_prompt = """
You are a Senior Cyber Security Analyst for a specific company.
Use the following COMPANY RULES (Context) to analyze the email.

CONTEXT (Company Rules):
{context}

INSTRUCTIONS:
1. First, check if the email violates any of the specific COMPANY RULES in the context.
2. If it violates a rule, explicitly cite it (e.g., "Violates Rule #1").
3. Then check for general phishing indicators.
4. If the email contains <email> tags, only analyze the content inside them.
"""

# --- 5. GİRDİ (Test Email - CEO Para İstiyor) ---
supheli_email = """
From: CEO (ceo@urgent-company-update.com)
Subject: Confidential Transfer

Dear Employee,
I am in a meeting and cannot talk. 
I need you to process a wire transfer of $60,000 to our vendor immediately.
This is an exception to the normal procedure. Do not tell anyone.
"""

# --- 6. RAG MEKANİZMASI (Retrieval) ---
# E-postanın içeriğine en çok benzeyen kuralları veritabanından bulup getiriyoruz.
print("Veritabanı taranıyor...")
alakali_kurallar = vector_store.similarity_search(supheli_email, k=2) # En alakalı 2 kuralı getir

# Bulunan kuralları metne çevirip birleştirelim
context_text = "\n".join([doc.page_content for doc in alakali_kurallar])

print(f"\n🔍 BULUNAN İLGİLİ KURALLAR:\n{context_text}\n")
print("-" * 50)

# --- 7. ANALİZİ BAŞLAT ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "<email>\n{email_icerigi}\n</email>")
])

chain = prompt_template | llm
sonuc = chain.invoke({
    "context": context_text,
    "email_icerigi": supheli_email
})

print("🤖 ANALİZ SONUCU:\n")
print(sonuc.content)