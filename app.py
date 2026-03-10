import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fake Review Detector", layout="wide")

def detect_fake(review):
    score = 0
    text = str(review).lower()
    if '!' in text and text.count('!') > 2: score += 3
    if str(review).isupper(): score += 3
    fake_words = ['perfect','amazing','best','love','5 stars','buy now','must buy']
    real_words = ['ok','average','decent','good but','works','fine']
    if any(w in text for w in fake_words): score += 2
    if any(w in text for w in real_words): score -= 2
    result = 'FAKE' if score >= 3 else 'REAL'
    confidence = min(95, max(50, 60 + score * 5))
    return result, confidence

st.title("🤖 Fake Review Detector")
st.markdown("**AI detects fake Amazon/Flipkart reviews** - Works with ANY CSV!")

tab1, tab2 = st.tabs(["📝 Single Review", "📊 CSV Analysis"])

with tab1:
    review = st.text_area("Paste review:", height=150, 
                         placeholder="OMG BEST PHONE EVER 5 STARS!!!!!")
    if st.button("🚀 Check if Fake!", use_container_width=True):
        if review.strip():
            label, conf = detect_fake(review)
            st.balloons()
            st.success(f"**{label}** | Confidence: **{conf}%**")
            st.markdown(f"> _{review}_")
        else:
            st.warning("Please type a review!")

with tab2:
    uploaded_file = st.file_uploader("Upload ANY CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write(f"📊 Found **{len(df)} rows** | **{len(df.columns)} columns**")
        
        # UPGRADE 1: Show all columns
        st.write("**Columns found:**", ", ".join(df.columns.tolist()))
        
        # UPGRADE 2: Auto-detect text columns
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not text_cols:
            st.error("❌ No text columns found! Add reviews as text.")
        else:
            st.success(f"✅ Found **{len(text_cols)} text columns**!")
            
            # Let user pick review column
            review_col = st.selectbox("Select review column:", text_cols)
            
            # Analyze selected column
            df[['result','confidence']] = df[review_col].fillna('').apply(
                lambda x: pd.Series(detect_fake(x)))
            
            st.dataframe(df[[review_col, 'result', 'confidence']].head(20), 
                        use_container_width=True)
            
            # UPGRADE 3: Better metrics
            fake_count = (df['result'] == 'FAKE').sum()
            total = len(df)
            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Total", total)
            col2.metric("❌ Fake", fake_count, f"{fake_count/total*100:.1f}%")
            col3.metric("✅ Real", total-fake_count)
            
            # UPGRADE 4: Download results
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Results", csv, "fake_review_results.csv")
