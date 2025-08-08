from typing import Literal
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

matplotlib.use("Agg")

# --- Financial Model Function ---
def calculate_margins_v29(
    medicare_mix: int,
    annual_volume: int,
    outpatient_shift_pct: int,
):
    # Assumptions
    car_t_drug_cost = 373000
    implementation_fee = 75000
    ch_monitoring_cost_per_day = 450
    ch_days = 15
    outpatient_monitoring_cost = ch_monitoring_cost_per_day * ch_days + implementation_fee
    outpatient_additional_cost = 15000  # labs, imaging, etc
    outpatient_total_cost = car_t_drug_cost + outpatient_monitoring_cost + outpatient_additional_cost
    outpatient_margin_per_patient = 381550

    # Inpatient cost ranges (Low and Mid only)
    inpatient_cost_low = car_t_drug_cost + 25000 + 15000 + 6000  # Facility + Staffing + Other
    inpatient_cost_mid = car_t_drug_cost + 32000 + 25000 + 12000
    inpatient_margin_low = 439000 - inpatient_cost_low
    inpatient_margin_mid = 488000 - inpatient_cost_mid

    # Blend payer mix
    medicare_ratio = medicare_mix / 100
    commercial_ratio = 1 - medicare_ratio

    shifted_patients = int((outpatient_shift_pct / 100) * annual_volume)

    # Calculate total financial improvement
    outpatient_total_margin = shifted_patients * outpatient_margin_per_patient

    improvement_low = outpatient_total_margin - (shifted_patients * inpatient_margin_mid)
    improvement_high = outpatient_total_margin - (shifted_patients * inpatient_margin_low)

    return {
        "impact_low": improvement_low,
        "impact_high": improvement_high,
        "shifted_patients": shifted_patients,
        "outpatient_margin_per_patient": outpatient_margin_per_patient,
        "inpatient_margin_range": (inpatient_margin_low, inpatient_margin_mid)
    }

# --- PDF Generation ---
def generate_pdf(mix, volume, shifted, impact_low, impact_high):
    template_reader = PdfReader("CAR-T_calculator_output3.pdf")
    writer = PdfWriter()
    writer.append(template_reader.pages[0])

    writer.update_page_form_field_values(writer.pages[0], {
        "payer_mix": f"{mix}%",
        "volume": f"{volume}",
        "shifted": f"{shifted}",
        "impact_range": f"${impact_low:,.0f} - ${impact_high:,.0f}"
    })

    output_pdf = BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)
    return output_pdf

# --- UI Configuration ---
st.set_page_config(page_title="CAR-T Calculator", layout="centered")
st.markdown(
    "<style>.main { background-color: #ffffff; }"
    "h1, h2, h3 { color: #110854; }"
    ".stButton button { background-color: #ff4861; color: white; font-weight: bold; }"
    ".stButton button:hover { background-color: #110854; }</style>",
    unsafe_allow_html=True
)

st.image("CH_Primary.png", width=160)
st.title("CAR-T Care Episode Financial Impact Estimator")

# --- User Inputs ---
payer_mix = st.slider("Medicare Payer Mix (%)", 0, 100, 50)
annual_volume = st.number_input("Annual CAR-T Patient Volume", min_value=1, step=1, value=500)
shift_pct = st.slider("Percent of Volume Shifted to Outpatient", 0, 100, 75)

# --- Calculate & Display ---
if st.button("See Impact"):
    result = calculate_margins_v29(payer_mix, annual_volume, shift_pct)
    st.markdown("### Your Estimated Financial Impact with Current Health:")
    st.markdown(
        f"<div style='color:#5842ff;font-size:32px;font-weight:bold;'>"
        f"${result['impact_low']:,.0f} - ${result['impact_high']:,.0f}</div>",
        unsafe_allow_html=True
    )
    st.caption("Range reflects shifting patients from a typical inpatient model to Current Health's outpatient episode.")

    if st.button("Download My Estimate"):
        pdf = generate_pdf(payer_mix, annual_volume, result['shifted_patients'], result['impact_low'], result['impact_high'])
        st.download_button("⬇️ Download My Estimate", data=pdf, file_name="CAR-T_Impact_Estimate.pdf", mime="application/pdf")
