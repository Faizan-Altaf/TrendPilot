import streamlit as st

st.set_page_config(
    page_title="TrendPilot AI",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 TrendPilot AI")
st.subheader("AI-Powered Content Creation Agent")

st.success("Streamlit is working correctly!")

st.markdown("""
Welcome to TrendPilot AI.

Your AI content assistant will help you create:
- Content ideas
- Social media captions
- Hashtags
- Video and Reel scripts
- Reviewed content saved to files
""")

topic = st.text_input(
    "What topic do you want to create content about?",
    placeholder="e.g. Artificial Intelligence"
)

platform = st.selectbox(
    "Choose your platform",
    ["LinkedIn", "Instagram", "YouTube"]
)

if st.button("Test Content Form"):
    if topic.strip():
        st.write("Topic:", topic)
        st.write("Platform:", platform)
        st.info("The interface is working. AI generation will be connected next.")
    else:
        st.warning("Please enter a topic first.")
