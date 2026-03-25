import streamlit as st
import PyPDF2
from groq import Groq

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(min(3, len(reader.pages))):
            text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def get_investment_signal(report_text):
    prompt = f"""
    Act as an Expert Equity Research Analyst for the Indian Market.
    Analyze this excerpt from a corporate filing:
    '{report_text}'

    Strictly follow these 'Opportunity Radar' rules:
    1. Signal Type: Is this an Opportunity, Risk, or Neutral?
    2. Actionable Decision: Buy, Sell, or Watch?
    3. Source-Cited Reasoning: Explain WHY based EXACTLY on the text provided. Mention the specific numbers or facts.
    4. Audit Trail: Explain your logical steps for this decision.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {e}"

#STREAMLIT UI
st.set_page_config(page_title="InvestRadar AI", page_icon="📈", layout="centered")

st.title("Opportunity Radar AI")
st.caption("Powered by Llama 3.1 | ET AI Hackathon 2026 - Track 6")
st.write("Upload any Indian Company's Corporate Filing (PDF) and let AI uncover hidden investment signals instantly.")

uploaded_file = st.file_uploader("Upload Quarterly Report / Filing (PDF)", type="pdf")

if uploaded_file is not None:
    with st.spinner("Reading PDF and extracting data..."):
        extracted_data = extract_text_from_pdf(uploaded_file)
    
    if "Error" not in extracted_data:
        with st.spinner("AI is analyzing the data for signals..."):
            result = get_investment_signal(extracted_data)
        
        st.success("Analysis Complete!")
        st.markdown("###AI Opportunity Signal")
        st.info(result)
        
        with st.expander("Show Raw Extracted Text (For Debugging)"):
            st.write(extracted_data[:1000] + "... [Text Truncated]")
    else:
        st.error(extracted_data)