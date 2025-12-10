# 🛡️ PhishGuard AI: Next-Gen Phishing Detection System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-Llama3-orange)
![Security](https://img.shields.io/badge/Security-RedTeam-red)

PhishGuard AI, kurum içi güvenlik politikalarını bilen (Context-Aware), prompt injection saldırılarına karşı korumalı ve RAG (Retrieval-Augmented Generation) teknolojisi ile güçlendirilmiş gelişmiş bir e-posta analiz aracıdır.

Klasik spam filtrelerinin aksine, PhishGuard e-postanın sadece "içeriğine" değil, "niyetine" ve "şirket kurallarına uygunluğuna" bakar.

<img width="1919" height="758" alt="image" src="https://github.com/user-attachments/assets/c32f3d4f-7613-4f3e-b3a8-105445a429a4" />


##  Özellikler

-  **RAG Teknolojisi:** Genel yapay zeka bilgisiyle yetinmez; Vektör Veritabanı (FAISS) kullanarak şirkete özel güvenlik kurallarını (PDF/Text) okur ve analizde referans gösterir.
-  **Prompt Injection Koruması:** Saldırganların yapay zekayı manipüle etmek için kullandığı "Ignore previous instructions" gibi komutları algılar ve engeller (Red Teaming Defence).
-  **Llama 3 & Groq:** Saniyeler içinde analiz yapmak için dünyanın en hızlı LLM altyapısını kullanır.
-  **Explainable AI (XAI):** Sadece "Zararlı" demez; nedenini madde madde, şirket kurallarına atıfta bulunarak açıklar.

##  Kullanılan Teknolojiler

* **LLM:** Meta Llama 3 (via Groq API)
* **Orchestration:** LangChain
* **Vector DB:** FAISS & HuggingFace Embeddings
* **Frontend:** Streamlit
* **Language:** Python

##  Kurulum ve Çalıştırma

Bu projeyi yerel bilgisayarınızda çalıştırmak için adımları takip edin:

1. **Repoyu Klonlayın**
   - git clone [https://github.com/utkankeser/PhishGuard-AI.git](https://github.com/utkankeser/PhishGuard-AI.git)
   - cd PhishGuard-AI
   
2. **Gerekli Kütüphaneleri Yükleyin**
   - pip install -r requirements.txt

3. **Veritabanını Oluşturun (RAG)**
   - python rag_setup.py

4. **Uygulamayı Başlatın**
   - streamlit run app.py

## Nasıl Çalışır?
1. Sol menüden Grog API Key girilir.
2. Analiz edilecek şüpheli e-posta metni kutuya yapıştırılır.
3. ANALIZ ET butonuna basılır.
4. Sistem, e-posta metnini hem genel phishing belirtilerine hem de “Şirket Anayasası” (Vector DB) ile karşılaştırır.
5. Sonuçlar ve ihlal edilen kurallar ekrana yansıtılır.

**Geliştirici Notu:** Bu proje, LLM Güvenliği ve RAG mimarileri üzerine yapılan bir Ar-Ge çalışmasının ürünüdür.
