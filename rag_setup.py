from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. ŞİRKET İÇİ GİZLİ KURALLAR (Knowledge Base)
# Normalde bunu bir PDF'ten okuruz, şimdilik elle yazıyoruz.
sirket_politikalari = [
    "KURAL 1: Şirket CEO'su asla e-posta ile para transferi istemez. Bu kesinlikle yasaktır.",
    "KURAL 2: IT Destek ekibi asla şifrenizi bir linke tıklayarak yenilemenizi istemez.",
    "KURAL 3: Acil durum tatbikatları sadece 'guvenlik@sirket.com' adresinden duyurulur.",
    "KURAL 4: 50.000 TL üzerindeki ödemeler için Islak İmza gereklidir, e-posta yetmez."
]

print("Veritabanı oluşturuluyor... (Modeller indiriliyor, bekleyin)")

# 2. EMBEDDING MODELİ (Metni Sayıya Çeviren Çevirmen)
# Bu model, kelimelerin anlamını vektör uzayına döker.
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. VERİLERİ VEKTÖRE ÇEVİR VE KAYDET (FAISS)
vector_store = FAISS.from_texts(sirket_politikalari, embeddings)

# Veritabanını yerel diske kaydedelim ki sonra tekrar tekrar oluşturmayalım.
vector_store.save_local("sirket_vektor_db")

print("✅ Başarılı! Kurallar 'sirket_vektor_db' klasörüne kaydedildi.")