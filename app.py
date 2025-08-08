
import streamlit as st
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

# --- UI/Styling ---
st.set_page_config(page_title="CAR-T Financial Calculator", layout="centered")
st.markdown("""
    <style>
        .stButton button {
            background-color: #ff4861;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        .stButton button:hover {
            background-color: #110854;
            color: white;
        }
        .big-number {
            font-size: 30px;
            color: #5842ff;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

st.image("CH_Primary.png", width=160)
st.title("CAR-T Episode Financial Impact Calculator")

# --- Input Fields ---
payer_mix = st.slider("Payer Mix (% Medicare)", 0, 100, 62)
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent Shifted to Outpatient", 0, 100, 75)

if st.button("See Impact"):

    # Reimbursement assumptions
    reimbursement = {
        "Medicare": {"Inpatient": 450000, "Outpatient": 430000},
        "Commercial": {"Inpatient": 550000, "Outpatient": 500000}
    }

    # Outpatient cost model
    outpatient_monitoring_cost = 450 * 15 + 75000
    outpatient_other = 15000
    outpatient_total = outpatient_monitoring_cost + outpatient_other

    # Inpatient cost range
    inpatient_low = 31000
    inpatient_high = 80000

    # Calculate margins
    def blended_margin(pct_medicare, site, cost=None):
        if site == "Outpatient":
            m_margin = reimbursement["Medicare"][site] - outpatient_total
            c_margin = reimbursement["Commercial"][site] - outpatient_total
        else:
            m_margin = reimbursement["Medicare"][site] - cost
            c_margin = reimbursement["Commercial"][site] - cost
        return (pct_medicare / 100) * m_margin + (1 - pct_medicare / 100) * c_margin

    # Calculate outputs
    shifted = round(patient_volume * shift_pct / 100)
    blended_out_margin = blended_margin(payer_mix, "Outpatient")
    margin_low = blended_margin(payer_mix, "Inpatient", inpatient_high)
    margin_high = blended_margin(payer_mix, "Inpatient", inpatient_low)

    impact_low = round(shifted * (blended_out_margin - margin_low))
    impact_high = round(shifted * (blended_out_margin - margin_high))

    impact_range_str = f"${impact_low:,.0f} - ${impact_high:,.0f}"

    # Output
    st.subheader("Your Estimated Financial Impact with Current Health:")
    st.markdown(f"<div class='big-number'>{impact_range_str}</div>", unsafe_allow_html=True)

    # DEBUG
    st.write("Debug - Inputs:")
    st.write(f"Payer Mix: {payer_mix}, Volume: {patient_volume}, Shifted: {shifted}")
    st.write(f"Outpatient Margin: {blended_out_margin:,.0f}")
    st.write(f"Inpatient Margin Range: {margin_low:,.0f} to {margin_high:,.0f}")
    st.write(f"Impact Range: {impact_low:,.0f} to {impact_high:,.0f}")

    # PDF Export
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=16, textColor="#5842ff"))

    flowables = [
        Paragraph("Your CAR-T Care Episode Impact Estimate", styles['CenterTitle']),
        Spacer(1, 20),
        Paragraph(f"Payer Mix: {payer_mix}% Medicare", styles['Normal']),
        Paragraph(f"Annual Volume: {patient_volume}", styles['Normal']),
        Paragraph(f"Outpatient Shift: {shifted} of {patient_volume} ({shift_pct}%)", styles['Normal']),
        Spacer(1, 10),
        Paragraph("Estimated Financial Improvement:", styles['Normal']),
        Paragraph(f"<font size=14 color='#5842ff'><b>{impact_range_str}</b></font>", styles['Normal']),
        Spacer(1, 20),
        Paragraph("Generated on: " + datetime.date.today().strftime("%B %d, %Y"), styles['Normal'])
    ]
    doc.build(flowables)
    buffer.seek(0)

    st.download_button(
        label="📄 Download My Estimate",
        data=buffer,
        file_name="Your_CART_Estimate.pdf",
        mime="application/pdf"
    )
