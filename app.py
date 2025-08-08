import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import base64

# App config
st.set_page_config(page_title="CAR-T Impact Estimator", layout="centered")

# Branding colors
PRIMARY_COLOR = "#5842ff"
CTA_COLOR = "#ff4861"
HOVER_COLOR = "#110854"
BACKGROUND_COLOR = "#E0E6EF"

# CSS Styling
st.markdown(f"""
    <style>
        .main {{ background-color: {BACKGROUND_COLOR}; }}
        h1, h2, h3 {{ color: {PRIMARY_COLOR}; }}
        .stButton button {{
            background-color: {CTA_COLOR};
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }}
        .stButton button:hover {{
            background-color: {HOVER_COLOR};
        }}
    </style>
""", unsafe_allow_html=True)

# Header
st.image("CH_Primary.png", width=160)
st.title("CAR-T Care Episode Financial Impact Estimator")

# Inputs
payer_mix_percent = st.slider("Medicare Payer Mix (%)", 0, 100, 50)
volume = st.number_input("Annual CAR-T Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent of Volume Shifted to Outpatient", 0, 100, 75)

# Derived values
shifted_patients = round(volume * (shift_pct / 100))
commercial_mix = 100 - payer_mix_percent

# Revenue assumptions
reimbursement_inpatient = (payer_mix_percent * 450000 + commercial_mix * 550000) / 100
reimbursement_outpatient = (payer_mix_percent * 430000 + commercial_mix * 500000) / 100

# Drug cost (fixed)
drug_cost = 373000

# Inpatient cost ranges
inpatient_cost_low = drug_cost + 10000 + 15000 + 6000
inpatient_cost_high = drug_cost + 25000 + 35000 + 20000

# Outpatient costs
ch_monitoring = 450 * 15
additional_outpatient_cost = 15000
implementation_fee_per_patient = 75000 / volume
outpatient_total_cost = drug_cost + ch_monitoring + additional_outpatient_cost + implementation_fee_per_patient

# Margins
inpatient_margin_low = reimbursement_inpatient - inpatient_cost_high
inpatient_margin_high = reimbursement_inpatient - inpatient_cost_low
outpatient_margin = reimbursement_outpatient - outpatient_total_cost

# Financial impact
impact_low = round((outpatient_margin - inpatient_margin_high) * shifted_patients)
impact_high = round((outpatient_margin - inpatient_margin_low) * shifted_patients)

# Display result
if st.button("See Impact"):
    st.markdown("### Your Estimated Financial Impact with Current Health:")
    styled_range = f"<div style='font-size: 32px; font-weight: bold; color: {CTA_COLOR};'>${impact_low:,.0f} - ${impact_high:,.0f}</div>"
    st.markdown(styled_range, unsafe_allow_html=True)

    # Load template PDF
    pdf_template_path = "CAR-T_calculator_output3.pdf"
    with open(pdf_template_path, "rb") as f:
        reader = PdfReader(f)
        writer = PdfWriter()
        first_page = reader.pages[0]
        writer.add_page(first_page)

        writer.update_page_form_field_values(writer.pages[0], {
            "payer_mix": f"{payer_mix_percent}%",
            "volume": f"{volume}",
            "shift_pct": f"{shift_pct}%",
            "impact_low": f"${impact_low:,.0f}",
            "impact_high": f"${impact_high:,.0f}",
        })

        output_pdf = BytesIO()
        writer.write(output_pdf)
        output_pdf.seek(0)

    # Generate download
    b64_pdf = base64.b64encode(output_pdf.read()).decode("utf-8")
    download_button = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Your_CAR-T_Impact_Estimate.pdf"><button style="background-color:{CTA_COLOR}; color:white; padding:8px 16px; font-size:16px; border:none; border-radius:5px;">Download My Estimate</button></a>'
    st.markdown(download_button, unsafe_allow_html=True)
