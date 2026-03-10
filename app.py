import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Fake Review Detector", layout="wide")

def detect_fake(review):
    score = 0
    text = review.lower()
    if review.count('!') > 2: score += 3
    if review.isupper(): score += 3
    if any(w in text for w in ['perfect','amazing','best','love','5 stars','buy now']): score += 2
    if any(w in text for w in ['ok','average','decent','good but','works']): score -= 2
    result = 'FAKE' if score >= 3 else 'REAL'
    confidence = min(95, max(50, 60 + score * 5))
    return result, confidence

st.title("🤖 Fake Review Detector")
st.markdown("**AI detects fake Amazon/Flipkart reviews** - Text or CSV upload")

tab1, tab2 = st.tabs(["📝 Single Review", "📊 CSV Analysis"])

with tab1:
    review = st.text_area("Paste review here:", height=150,
                         placeholder="OMG BEST PHONE EVER 5 STARS!!!!!")
    col1, col2 = st.columns([3,1])
    with col1:
        if st.button("🚀 Check if Fake!", use_container_width=True):
            if review.strip():
                label, conf = detect_fake(review)
                st.balloons()
                st.success(f"**{label}** | Confidence: **{conf}%**")
                st.markdown(f"> _{review}_")
            else:
                st.warning("Please type a review!")
    
with tab2:
    uploaded_file = st.file_uploader("Upload CSV (must have 'review' column)", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'review' in df.columns:
            df[['result', 'confidence']] = df['review'].fillna('').apply(
                lambda x: pd.Series(detect_fake(x)))
            
            st.dataframe(df[['review', 'result', 'confidence']].head(20), 
                        use_container_width=True)
            
            fake_count = (df['result'] == 'FAKE').sum()
            total = len(df)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Reviews", total)
            col2.metric("Fake Reviews", fake_count, f"{fake_count/total*100:.1f}%")
            col3.metric("Real Reviews", total-fake_count)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Results", csv, "fake_review_results.csv")
        else:
            st.error("❌ CSV must have a **'review'** column!")
