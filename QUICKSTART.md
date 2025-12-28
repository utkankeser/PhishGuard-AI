# 🚀 Quick Setup Guide - PhishGuard AI

Follow these steps to get PhishGuard AI up and running in 5 minutes!

## Step 1️⃣: Install Dependencies

```bash
pip install -r requirements.txt
```

⏱️ **Expected time**: 2-3 minutes (depending on internet speed)

## Step 2️⃣: Configure API Key

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Get your Groq API key from [console.groq.com](https://console.groq.com/keys)

3. Open `.env` and replace `your_groq_api_key_here` with your actual key:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```

## Step 3️⃣: Initialize Vector Database

```bash
python rag_setup.py
```

⏱️ **Expected time**: 1-2 minutes (first-time model download)

✅ You should see: `✅ Setup Complete!`

## Step 4️⃣: Test the System

### Option A: Web Interface (Recommended)

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser

### Option B: Command Line

```bash
python phish_guard_rag.py
```

## 🎉 That's It!

You're now ready to analyze phishing emails!

---

## 📝 Quick Test

Try analyzing this sample phishing email:

```
From: ceo@urgent-company-update.com
Subject: URGENT: Wire Transfer Needed

Dear Employee,
I need you to process a wire transfer of $50,000 immediately.
This is confidential. Do not call me.
```

The system should detect it as phishing and cite company rules!

---

## ⚠️ Troubleshooting

### Issue: `No module named 'colorlog'`
**Fix**: Run `pip install -r requirements.txt`

### Issue: `Vector database not found`
**Fix**: Run `python rag_setup.py`

### Issue: `API key not configured`
**Fix**: Make sure you've set `GROQ_API_KEY` in your `.env` file

### Issue: Logs directory not created
**Fix**: The system creates it automatically, but you can manually create: `mkdir logs`

---

For detailed documentation, see [README.md](README.md)
