# 🤖 AI Product Manager
**Intelligent Product Insight & Feature Recommendation System**

A Final Year AIML Project — live, deployable, and usable in under 30 minutes.

---

## 🚀 Run Locally (5 minutes)

```bash
# 1. Clone or download this folder
# 2. Open terminal in the folder

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py

# App opens at http://localhost:8501
```

---

## ☁️ Deploy Live on Streamlit Cloud (10 minutes) — FREE

1. Push this folder to a **GitHub repo** (public or private)
2. Go to **https://share.streamlit.io**
3. Sign in with GitHub
4. Click **"New app"**
5. Select your repo → branch → set `app.py` as main file
6. Click **"Deploy"**
7. ✅ You get a live URL like: `https://yourname-aipm.streamlit.app`

---

## 📁 Project Structure

```
aipm_app/
├── app.py            ← Main Streamlit application
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## 🧠 What It Does

| Step | What Happens |
|------|-------------|
| Upload | CSV file, paste text, or use sample data |
| Clean  | Auto-clean, lowercase, Hinglish normalize |
| Sentiment | Custom NLP — Positive / Negative / Neutral |
| Pain Points | Keyword-based detection from negative reviews |
| Recommendations | Feature suggestions with priority scores |
| Roadmap | Q1/Q2/Q3 roadmap based on priority |
| Export | Download results as CSV |

---

## ✅ Features
- 📤 CSV upload + text paste + sample data
- 😊 Sentiment analysis with score distribution chart
- 🔥 Pain point detection (keyword-based)
- 💡 Feature recommendations with priority score (0–100)
- 🗺️ Auto-generated product roadmap (Q1/Q2/Q3)
- 📊 Interactive Plotly charts
- ⬇️ Export results to CSV
- 🇮🇳 Hinglish review support

---

## 🛠️ Tech Stack
- **Frontend/Backend**: Streamlit (Python)
- **NLP**: Custom sentiment engine (no external API needed)
- **Visualization**: Plotly
- **Data**: Pandas
- **Deployment**: Streamlit Cloud (free)

---

## 📬 Built By
Final Year AIML Student — AI Product Manager Project
