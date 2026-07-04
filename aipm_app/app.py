import streamlit as st
import pandas as pd
import re
import time
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Product Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-title {
        color: #6B7280;
        font-size: 1rem;
        margin-top: 4px;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1E293B;
        border-left: 4px solid #2563EB;
        padding-left: 12px;
        margin: 24px 0 12px 0;
    }
    .rec-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border-left: 5px solid;
    }
    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .footer {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.78rem;
        padding: 24px 0 8px 0;
        border-top: 1px solid #F1F5F9;
        margin-top: 32px;
    }
</style>
""", unsafe_allow_html=True)

# ── Hinglish dictionary ──────────────────────────────────────────────
HINGLISH = {
    'bekar': 'useless', 'bakwaas': 'nonsense', 'accha': 'good',
    'achha': 'good', 'bahut': 'very', 'ekdum': 'completely',
    'thoda': 'little', 'khatam': 'finished', 'fail': 'failed',
    'problem': 'problem', 'bura': 'bad', 'ganda': 'bad',
    'mast': 'great', 'zabardast': 'excellent', 'bekaar': 'useless',
    'seedha': 'directly', 'bilkul': 'absolutely', 'nahi': 'not',
    'nhi': 'not', 'hai': 'is', 'tha': 'was', 'acha': 'good',
}

# ── Pain → Feature map ───────────────────────────────────────────────
PAIN_MAP = {
    'crash':        ('Fix app stability and crash bugs',        3),
    'crashes':      ('Fix app stability and crash bugs',        3),
    'slow':         ('Optimize performance and loading speed',  2),
    'lag':          ('Optimize performance and loading speed',  2),
    'payment':      ('Improve payment gateway reliability',     3),
    'upi':          ('Add seamless UPI / multi-payment support',3),
    'login':        ('Fix login and authentication flow',       3),
    'offline':      ('Add offline mode for key features',       2),
    'video':        ('Improve video streaming and quality',     2),
    'battery':      ('Optimize battery consumption',            1),
    'support':      ('Improve customer support response time',  2),
    'notification': ('Fix notification delivery system',        1),
    'search':       ('Improve in-app search functionality',     2),
    'price':        ('Revisit pricing — add affordable tiers',  2),
    'update':       ('Improve update process and changelog',    1),
    'download':     ('Add download and save for offline',       2),
    'interface':    ('Redesign UI for simplicity',              2),
    'ui':           ('Redesign UI for simplicity',              2),
    'bug':          ('Fix reported bugs systematically',        3),
    'error':        ('Improve error handling and messages',     3),
    'account':      ('Fix account management and sync',         2),
    'data':         ('Improve data backup and sync',            2),
    'subscription': ('Simplify subscription management',        2),
    'useless':      ('Improve core product value',              3),
    'nonsense':     ('Improve core product value',              3),
    'failed':       ('Fix reliability and failure modes',       3),
    'broken':       ('Fix critical broken functionality',       3),
    'refund':       ('Improve refund and billing process',      2),
    'ads':          ('Reduce intrusive ad experience',          1),
    'dark mode':    ('Add dark mode support',                   1),
    'language':     ('Add multi-language support',              1),
}

# ── VADER-like simple sentiment (no install needed) ──────────────────
POSITIVE_WORDS = {
    'good','great','excellent','amazing','love','best','perfect','awesome',
    'fantastic','superb','wonderful','outstanding','brilliant','helpful',
    'easy','simple','fast','smooth','nice','beautiful','recommend','happy',
    'satisfied','useful','efficient','intuitive','clean','responsive','quick',
    'reliable','stable','solid','brilliant','cool','neat','super','wow',
}
NEGATIVE_WORDS = {
    'bad','terrible','horrible','worst','hate','poor','awful','useless',
    'broken','crash','crashes','crashing','bug','slow','lag','fail','failed',
    'error','problem','issue','waste','disappoint','frustrated','frustrating',
    'annoying','stupid','pathetic','garbage','trash','uninstall','wrong',
    'fake','spam','never','remove','delete','avoid','freeze','freezes',
    'hang','dead','missing','unable','stuck','constantly','dreadful','dire',
}
INTENSIFIERS = {
    'very':1.5,'really':1.4,'extremely':1.8,'so':1.3,
    'totally':1.5,'absolutely':1.6,'completely':1.5,'highly':1.3,
}
NEGATORS = {'not','no','never','dont',"don't",'cant',"can't",'isnt',"isn't",'wasnt',"wasn't"}

def get_sentiment(text: str):
    words = re.findall(r'\b\w+\b', str(text).lower())
    # Apply hinglish map
    words = [HINGLISH.get(w, w) for w in words]

    score = 0.0
    i = 0
    while i < len(words):
        word = words[i]
        multiplier = 1.0
        negate = False

        # Check previous word for intensifier/negator
        if i > 0:
            prev = words[i-1]
            if prev in INTENSIFIERS:
                multiplier = INTENSIFIERS[prev]
            if prev in NEGATORS:
                negate = True

        if word in POSITIVE_WORDS:
            delta = 1.0 * multiplier
            score += (-delta if negate else delta)
        elif word in NEGATIVE_WORDS:
            delta = 1.0 * multiplier
            score += (delta if negate else -delta)  # negating negative = positive
        i += 1

    # Normalize to -1 to +1
    word_count = max(len(words), 1)
    normalized = max(-1.0, min(1.0, score / (word_count ** 0.5)))

    if normalized >= 0.1:
        label = 'Positive'
    elif normalized <= -0.1:
        label = 'Negative'
    else:
        label = 'Neutral'
    return label, round(normalized, 3)


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', '', text)
    words = text.split()
    words = [HINGLISH.get(w, w) for w in words]
    return ' '.join(words).strip()


def extract_pain_keywords(texts: list) -> list:
    all_text = ' '.join([clean_text(t) for t in texts])
    found = {}
    for keyword, (feature, weight) in PAIN_MAP.items():
        count = all_text.count(keyword)
        if count > 0:
            if feature not in found:
                found[feature] = {'keyword': keyword, 'count': count, 'weight': weight}
            else:
                found[feature]['count'] += count
    return sorted(found.items(), key=lambda x: x[1]['count'] * x[1]['weight'], reverse=True)


def priority_score(count: int, weight: int, total: int) -> int:
    frequency = min(50, int((count / max(total, 1)) * 200))
    severity = weight * 15
    base = 30
    return min(100, base + frequency + severity)


def get_sample_df() -> pd.DataFrame:
    return pd.DataFrame({'review_text': [
        "App crashes every time I try to open it. Very frustrating experience.",
        "Payment fails constantly. UPI doesn't work at all. Please fix asap!",
        "Great app overall but it loads very slowly on mobile data.",
        "Excellent features! Best app I have used in a long time.",
        "Login does not work after the latest update. Completely broken.",
        "Video quality is very poor and it buffers every few seconds.",
        "Amazing app, highly recommend to everyone. Very helpful.",
        "No offline mode available. Please add this feature soon.",
        "Battery drains so fast when using this. Major issue.",
        "Customer support is very slow. Took 5 days to respond.",
        "Interface is confusing and not intuitive at all.",
        "Love the search feature, works perfectly every time!",
        "Subscription keeps getting cancelled without reason. Refund please!",
        "App freezes on the checkout page. Lost my order twice.",
        "Superb performance after the update. Much faster now.",
        "Bug in the notification system. Not receiving alerts.",
        "Very easy to use and clean interface. Good job team!",
        "Download feature is broken. Files don't save offline.",
        "Worst app ever. Uninstalling after this terrible experience.",
        "Really smooth and reliable. No crashes in 3 months.",
    ]})


# ═══════════════════════════════════════════════════════════════════════
# UI LAYOUT
# ═══════════════════════════════════════════════════════════════════════

# Header
st.markdown('<div class="main-title">🤖 AI Product Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Product Insight & Feature Recommendation System</div>', unsafe_allow_html=True)
st.markdown("")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    n_recs = st.slider("Max feature recommendations", 3, 10, 5)
    show_raw = st.checkbox("Show raw review data")
    st.markdown("---")
    st.markdown("### 🧠 How it works")
    st.markdown("""
1. 📤 Upload reviews
2. 🧹 Auto clean & process
3. 😊 Sentiment analysis
4. 🔍 Pain point detection
5. 💡 Feature recommendations
6. 📊 Priority scoring
""")
    st.markdown("---")
    st.markdown("### 📦 Built With")
    st.markdown("Streamlit · VADER-style NLP · TF-IDF · Python")

# ─── INPUT SECTION ───────────────────────────────────────────────────
st.markdown('<div class="section-header">📤 Step 1 — Load Your Reviews</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📁 Upload CSV", "✏️ Paste Text", "🎯 Use Sample Data"])

df = None

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded = st.file_uploader("Upload a CSV file with customer reviews", type=['csv'])
        if uploaded:
            try:
                temp_df = pd.read_csv(uploaded)
                # Auto-detect text column
                text_col = None
                for col in temp_df.columns:
                    if col.lower() in ['review','text','review_text','comment','feedback','content','description']:
                        text_col = col
                        break
                if not text_col:
                    text_col = st.selectbox("Select the column with review text:", temp_df.columns.tolist())
                else:
                    st.success(f"✅ Auto-detected review column: **{text_col}**")
                temp_df['review_text'] = temp_df[text_col].astype(str)
                df = temp_df
            except Exception as e:
                st.error(f"Could not read file: {e}")

    with col2:
        st.markdown("**Expected format:**")
        st.code("review_text\nApp crashes often!\nLove the UI!\nPayment fails...")
        sample_csv = get_sample_df().to_csv(index=False).encode()
        st.download_button("⬇️ Download sample CSV", sample_csv, "sample_reviews.csv", "text/csv")

with tab2:
    pasted = st.text_area(
        "Paste reviews — one per line",
        height=180,
        placeholder="App crashes every time I open it.\nPayment keeps failing. Very frustrating!\nGreat app, love the features.\nVery slow and laggy on older phones."
    )
    if pasted.strip():
        lines = [l.strip() for l in pasted.strip().split('\n') if len(l.strip()) > 5]
        if lines:
            df = pd.DataFrame({'review_text': lines})

with tab3:
    st.info("👇 Click below to load 20 sample reviews and see the system in action.")
    if st.button("🚀 Load Sample Reviews", type="primary"):
        df = get_sample_df()
        st.success("✅ 20 sample reviews loaded!")

# ─── ANALYSIS ────────────────────────────────────────────────────────
if df is not None:
    df['review_text'] = df['review_text'].fillna('').astype(str)
    df = df[df['review_text'].str.len() > 4].reset_index(drop=True)

    st.markdown("")
    col_info, col_btn = st.columns([3, 1])
    col_info.markdown(f"✅ **{len(df)} reviews** ready for analysis")

    analyse = col_btn.button("🔍 Analyse Now", type="primary", use_container_width=True)

    if analyse or st.session_state.get('analysed'):
        st.session_state['analysed'] = True

        if analyse:  # Re-run fresh
            with st.spinner(""):
                bar = st.progress(0, text="🧹 Cleaning text...")
                df['clean'] = df['review_text'].apply(clean_text)
                bar.progress(25, text="😊 Running sentiment analysis...")
                sentiment_results = df['review_text'].apply(get_sentiment)
                df['sentiment'] = sentiment_results.apply(lambda x: x[0])
                df['score'] = sentiment_results.apply(lambda x: x[1])
                bar.progress(55, text="🔍 Detecting pain points...")
                negative_reviews = df[df['sentiment'] == 'Negative']['review_text'].tolist()
                all_reviews = df['review_text'].tolist()
                pain_items = extract_pain_keywords(negative_reviews if negative_reviews else all_reviews)
                bar.progress(80, text="💡 Generating recommendations...")
                bar.progress(100, text="✅ Done!")
                time.sleep(0.4)
                bar.empty()
            st.session_state['df'] = df
            st.session_state['pain_items'] = pain_items

        df = st.session_state.get('df', df)
        pain_items = st.session_state.get('pain_items', [])

        # ─── RESULTS ─────────────────────────────────────────────────
        st.markdown('<div class="section-header">📊 Step 2 — Sentiment Overview</div>', unsafe_allow_html=True)

        pos_count = (df['sentiment'] == 'Positive').sum()
        neg_count = (df['sentiment'] == 'Negative').sum()
        neu_count = (df['sentiment'] == 'Neutral').sum()
        total = len(df)
        avg_score = df['score'].mean()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📋 Total Reviews", total)
        c2.metric("😊 Positive", f"{pos_count}", f"{int(pos_count/total*100)}%")
        c3.metric("😐 Neutral", f"{neu_count}", f"{int(neu_count/total*100)}%")
        c4.metric("😞 Negative", f"{neg_count}", f"{int(neg_count/total*100)}%")
        mood = "🟢 Positive" if avg_score > 0.1 else "🔴 Negative" if avg_score < -0.1 else "🟡 Mixed"
        c5.metric("🧠 Overall Mood", mood)

        # Charts
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Sentiment breakdown**")
            fig_pie = px.pie(
                names=['Positive', 'Neutral', 'Negative'],
                values=[pos_count, neu_count, neg_count],
                color=['Positive', 'Neutral', 'Negative'],
                color_discrete_map={
                    'Positive': '#059669',
                    'Neutral': '#6B7280',
                    'Negative': '#DC2626'
                },
                hole=0.45,
            )
            fig_pie.update_layout(
                height=280, margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation='h', y=-0.15)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            st.markdown("**Sentiment score distribution**")
            fig_hist = px.histogram(
                df, x='score', nbins=20,
                color_discrete_sequence=['#2563EB'],
                labels={'score': 'Sentiment score (−1 negative → +1 positive)'}
            )
            fig_hist.add_vline(x=0, line_dash='dash', line_color='#DC2626', annotation_text="Neutral")
            fig_hist.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)

        # ─── PAIN POINTS ─────────────────────────────────────────────
        st.markdown('<div class="section-header">🔥 Step 3 — Detected Pain Points</div>', unsafe_allow_html=True)

        if pain_items:
            pain_df = pd.DataFrame([
                {
                    'Issue': feat,
                    'Mentions': data['count'],
                    'Keyword': data['keyword'],
                }
                for feat, data in pain_items[:8]
            ])

            fig_bar = px.bar(
                pain_df, x='Mentions', y='Issue',
                orientation='h',
                color='Mentions',
                color_continuous_scale='Reds',
                text='Mentions'
            )
            fig_bar.update_traces(textposition='outside')
            fig_bar.update_layout(
                height=max(280, len(pain_df) * 48),
                margin=dict(t=10, b=10, l=10, r=10),
                yaxis=dict(autorange='reversed'),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.success("🎉 No major pain points detected — your users seem happy!")

        # ─── FEATURE RECOMMENDATIONS ─────────────────────────────────
        st.markdown('<div class="section-header">💡 Step 4 — Feature Recommendations</div>', unsafe_allow_html=True)

        if pain_items:
            for rank, (feat, data) in enumerate(pain_items[:n_recs]):
                pscore = priority_score(data['count'], data['weight'], total)

                if pscore >= 70:
                    badge = "🔴 CRITICAL"
                    border_color = "#DC2626"
                    bg = "#FFF5F5"
                elif pscore >= 50:
                    badge = "🟡 HIGH"
                    border_color = "#F59E0B"
                    bg = "#FFFBEB"
                else:
                    badge = "🟢 MEDIUM"
                    border_color = "#059669"
                    bg = "#F0FDF4"

                with st.expander(f"#{rank+1}  {feat}  |  {badge}  |  Score: {pscore}/100"):
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Priority Score", f"{pscore}/100")
                    m2.metric("Mentions in Reviews", data['count'])
                    m3.metric("Impact Level", badge.split()[1])
                    est_churn = min(25, data['count'] * 2)
                    m4.metric("Est. Churn Reduction", f"~{est_churn}%")
                    st.progress(pscore / 100)
                    st.markdown(f"**Pain keyword detected:** `{data['keyword']}`")
                    st.markdown(
                        f"**Recommended action:** Prioritise this in your next sprint. "
                        f"Fixing this could improve your app rating and reduce negative reviews."
                    )
        else:
            st.success("No critical issues detected from the review data.")

        # ─── ROADMAP ─────────────────────────────────────────────────
        st.markdown('<div class="section-header">🗺️ Step 5 — Suggested Product Roadmap</div>', unsafe_allow_html=True)

        if pain_items:
            roadmap = []
            for feat, data in pain_items[:n_recs]:
                ps = priority_score(data['count'], data['weight'], total)
                quarter = "Q1 — Now" if ps >= 70 else "Q2 — Next" if ps >= 50 else "Q3 — Later"
                roadmap.append({'Feature': feat[:45], 'Priority': ps, 'Quarter': quarter})

            rdf = pd.DataFrame(roadmap)
            fig_road = px.bar(
                rdf, x='Priority', y='Feature',
                orientation='h',
                color='Quarter',
                color_discrete_map={
                    'Q1 — Now': '#DC2626',
                    'Q2 — Next': '#F59E0B',
                    'Q3 — Later': '#059669'
                },
                text='Priority'
            )
            fig_road.update_traces(texttemplate='%{text}/100', textposition='outside')
            fig_road.update_layout(
                xaxis_range=[0, 120],
                height=max(280, len(roadmap) * 52),
                margin=dict(t=10, b=10, l=10, r=10),
                yaxis=dict(autorange='reversed'),
                legend=dict(title='Build when', orientation='h', y=-0.2)
            )
            st.plotly_chart(fig_road, use_container_width=True)

        # ─── EXPORT ──────────────────────────────────────────────────
        st.markdown('<div class="section-header">📄 Step 6 — Export Results</div>', unsafe_allow_html=True)

        ec1, ec2 = st.columns(2)
        with ec1:
            export = df[['review_text', 'sentiment', 'score']].copy()
            export.columns = ['Review', 'Sentiment', 'Score']
            st.download_button(
                "⬇️ Download analysed reviews (CSV)",
                export.to_csv(index=False).encode(),
                "analysed_reviews.csv", "text/csv", use_container_width=True
            )
        with ec2:
            if pain_items:
                rec_export = pd.DataFrame([{
                    'Feature Recommendation': f,
                    'Mentions': d['count'],
                    'Priority Score': priority_score(d['count'], d['weight'], total),
                    'Keyword': d['keyword'],
                } for f, d in pain_items[:n_recs]])
                st.download_button(
                    "⬇️ Download recommendations (CSV)",
                    rec_export.to_csv(index=False).encode(),
                    "recommendations.csv", "text/csv", use_container_width=True
                )

        # ─── RAW DATA ────────────────────────────────────────────────
        if show_raw:
            st.markdown('<div class="section-header">🔍 Raw Review Data</div>', unsafe_allow_html=True)
            st.dataframe(
                df[['review_text', 'sentiment', 'score']].rename(
                    columns={'review_text': 'Review', 'sentiment': 'Sentiment', 'score': 'Score'}
                ),
                use_container_width=True, height=300
            )

# ─── FOOTER ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">🤖 AI Product Manager · Final Year AIML Project · '
    'Built with Streamlit, Python, NLP</div>',
    unsafe_allow_html=True
)
