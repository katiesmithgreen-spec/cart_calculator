
import streamlit as st
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

st.image("CH_Primary.png", width=160)
st.title("CAR-T Episode Financial Impact Calculator")

# Initialize session state
if "show_results" not in st.session_state:
    st.session_state.show_results = False

payer_mix = st.slider("Payer Mix (% Medicare)", 0, 100, 62)
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent Shifted to Outpatient", 0, 100, 75)

# Mock financial impact logic
shifted_patients = round(patient_volume * shift_pct / 100)
impact_low = 2100000
impact_high = 6700000
impact_range_str = f"${impact_low:,} to ${impact_high:,}"

if st.button("See Impact"):
    st.session_state.show_results = True

if st.session_state.show_results:
    st.subheader("Estimated Financial Impact")
    st.markdown(f'''
- **Payer Mix:** {payer_mix}% Medicare  
- **Patient Volume:** {patient_volume}  
- **Outpatient Shift:** {shifted_patients} of {patient_volume} patients ({shift_pct}%)  
- **Estimated Financial Improvement:**  
  <span style='font-size: 24px; color: #5842ff'><b>{impact_range_str}</b></span>
''', unsafe_allow_html=True)

    if st.button("📄 Download My Estimate"):

        # Generate personalized PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=LETTER)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=16, textColor="#5842ff"))

        flowables = [
            Paragraph("Your CAR-T Care Episode Impact Estimate", styles['CenterTitle']),
            Spacer(1, 20),
            Paragraph(f"<b>Payer Mix:</b> {payer_mix}% Medicare", styles['Normal']),
            Paragraph(f"<b>Annual Volume:</b> {patient_volume}", styles['Normal']),
            Paragraph(f"<b>Outpatient Shift:</b> {shifted_patients} of {patient_volume} ({shift_pct}%)", styles['Normal']),
            Spacer(1, 10),
            Paragraph(f"<b>Estimated Financial Improvement:</b>", styles['Normal']),
            Paragraph(f"<font size=14 color='#5842ff'><b>{impact_range_str}</b></font>", styles['Normal']),
            Spacer(1, 20),
            Paragraph("Generated on: " + datetime.date.today().strftime("%B %d, %Y"), styles['Normal'])
        ]

        doc.build(flowables)
        buffer.seek(0)

        st.download_button(
            label="Download PDF",
            data=buffer,
            file_name="Your_CART_Estimate.pdf",
            mime="application/pdf"
        )
