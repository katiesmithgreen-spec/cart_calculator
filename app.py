
import streamlit as st
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

# --- Branding and Style ---
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
            font-size: 28px;
            color: #5842ff;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

st.image("CH_Primary.png", width=160)
st.title("CAR-T Episode Financial Impact Calculator")

# --- Inputs ---
if "show_results" not in st.session_state:
    st.session_state.show_results = False

payer_mix = st.slider("Payer Mix (% Medicare)", 0, 100, 62)
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent Shifted to Outpatient", 0, 100, 75)

# --- Core Logic ---
shifted_patients = round(patient_volume * shift_pct / 100)

# Static reimbursement values
reimbursement = {
    "Medicare": {"Inpatient": 450000, "Outpatient": 430000},
    "Commercial": {"Inpatient": 550000, "Outpatient": 500000}
}

# Outpatient cost model
ch_daily_cost = 450
ch_days = 15
ch_impl_fee = 75000
other_outpatient_cost = 15000
total_ch_cost = ch_days * ch_daily_cost + ch_impl_fee
outpatient_total_cost = total_ch_cost + other_outpatient_cost

# Inpatient cost range (low/high)
inpatient_low = 31000
inpatient_high = 80000

def blended_margin(p_mix, inpatient_cost):
    med_margin = reimbursement["Medicare"]["Inpatient"] - inpatient_cost
    comm_margin = reimbursement["Commercial"]["Inpatient"] - inpatient_cost
    return (p_mix / 100 * med_margin) + ((100 - p_mix) / 100 * comm_margin)

blended_inpatient_margin_low = blended_margin(payer_mix, inpatient_high)
blended_inpatient_margin_high = blended_margin(payer_mix, inpatient_low)

# Outpatient margin per patient
blended_out_margin = (
    (payer_mix / 100) * (reimbursement["Medicare"]["Outpatient"] - outpatient_total_cost) +
    ((100 - payer_mix) / 100) * (reimbursement["Commercial"]["Outpatient"] - outpatient_total_cost)
)

# Total impact range
impact_low = round(shifted_patients * (blended_out_margin - blended_inpatient_margin_low))
impact_high = round(shifted_patients * (blended_out_margin - blended_inpatient_margin_high))
impact_range_str = f"${impact_low:,.0f} - ${impact_high:,.0f}"

# --- UI Output ---
if st.button("See Impact"):
    st.session_state.show_results = True

if st.session_state.show_results:
    st.subheader("Your Estimated Financial Impact with Current Health:")
    st.markdown(
        f"<p><strong>Payer Mix:</strong> {payer_mix}% Medicare</p>"
        f"<p><strong>Patient Volume:</strong> {patient_volume}</p>"
        f"<p><strong>Outpatient Shift:</strong> {shifted_patients} of {patient_volume} patients ({shift_pct}%)</p>"
        f"<p><strong>Estimated Financial Improvement:</strong></p>"
        f"<div class='big-number'>{impact_range_str}</div>",
        unsafe_allow_html=True
    )

    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=16, textColor="#5842ff"))

    flowables = [
        Paragraph("Your CAR-T Care Episode Impact Estimate", styles['CenterTitle']),
        Spacer(1, 20),
        Paragraph(f"Payer Mix: {payer_mix}% Medicare", styles['Normal']),
        Paragraph(f"Annual Volume: {patient_volume}", styles['Normal']),
        Paragraph(f"Outpatient Shift: {shifted_patients} of {patient_volume} ({shift_pct}%)", styles['Normal']),
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
