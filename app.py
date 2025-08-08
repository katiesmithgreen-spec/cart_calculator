
import streamlit as st
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

# --- Styling ---
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

# Logo
st.image("CH_Primary.png", width=160)

st.title("CAR-T Episode Financial Impact Calculator")

# --- Input Fields ---
payer_mix = st.slider("Payer Mix (% Medicare)", 0, 100, 62)
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent Shifted to Outpatient", 0, 100, 75)

# --- Financial Constants ---
reimbursement = {
    "Medicare": {"Inpatient": 450000, "Outpatient": 430000},
    "Commercial": {"Inpatient": 550000, "Outpatient": 500000}
}

# Cost estimates
inpatient_cost_range = (31000, 80000)  # low, high
outpatient_monitoring_cost = 450 * 15 + 75000  # Daily cost * 15 + implementation
outpatient_other = 15000
outpatient_total = outpatient_monitoring_cost + outpatient_other

# Margin Calculations
def blended_margin(pct_medicare, site, inpatient_cost=None):
    if site == "Outpatient":
        margin_medicare = reimbursement["Medicare"][site] - outpatient_total
        margin_commercial = reimbursement["Commercial"][site] - outpatient_total
    else:
        margin_medicare = reimbursement["Medicare"][site] - inpatient_cost
        margin_commercial = reimbursement["Commercial"][site] - inpatient_cost
    return ((pct_medicare / 100) * margin_medicare +
            ((100 - pct_medicare) / 100) * margin_commercial)

shifted = round(patient_volume * shift_pct / 100)
low_margin_diff = blended_margin(payer_mix, "Outpatient") - blended_margin(payer_mix, "Inpatient", inpatient_cost_range[1])
high_margin_diff = blended_margin(payer_mix, "Outpatient") - blended_margin(payer_mix, "Inpatient", inpatient_cost_range[0])
impact_low = round(shifted * low_margin_diff)
impact_high = round(shifted * high_margin_diff)

# --- Display Results ---
if st.button("See Impact"):
    st.subheader("Your Estimated Financial Impact with Current Health:")
    st.markdown(f"""
    **Payer Mix:** {payer_mix}% Medicare  
    **Patient Volume:** {patient_volume}  
    **Shifted to Outpatient:** {shifted} patients  
    **Estimated Financial Improvement:**  
    <div class='big-number'>${impact_low:,.0f} - ${impact_high:,.0f}</div>
    """, unsafe_allow_html=True)

    # --- PDF Output ---
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
        Paragraph(f"<font size=14 color='#5842ff'><b>${impact_low:,.0f} - ${impact_high:,.0f}</b></font>", styles['Normal']),
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
