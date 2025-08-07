
from typing import Literal
import streamlit as st

from PIL import Image
import matplotlib
matplotlib.use('Agg')

# --- Financial Model Function ---
def car_t_financial_model(
    medicare_pct: int = 50,
    inpatient_los_days: int = 10,
    readmission_rate: float = 0.15,
    patient_volume: int = 500,
    outpatient_shift_pct: int = 75
):
    car_t_drug_cost = 373000

    reimbursement = {
        'Medicare': {'Inpatient': 450000, 'Outpatient': 430000},
        'Commercial': {'Inpatient': 550000, 'Outpatient': 500000}
    }

    medicare_share = medicare_pct / 100
    commercial_share = 1 - medicare_share

    inpatient_reimbursement = (
        commercial_share * reimbursement['Commercial']['Inpatient'] +
        medicare_share * reimbursement['Medicare']['Inpatient']
    )
    outpatient_reimbursement = (
        commercial_share * reimbursement['Commercial']['Outpatient'] +
        medicare_share * reimbursement['Medicare']['Outpatient']
    )

    # Outpatient Costs
    current_health_cost = 450 * 15
    implementation_fee = 75000
    additional_outpatient_cost = 15000
    outpatient_cost = car_t_drug_cost + current_health_cost + additional_outpatient_cost
    outpatient_margin = outpatient_reimbursement - outpatient_cost
    amortized_outpatient_margin = outpatient_margin - (implementation_fee / patient_volume)

    # Inpatient Margin (realistic range to allow negative margins)
    def margin_range():
        facility = (18000, 28000)
        staffing = (25000, 38000)
        services = (10000, 20000)
        readmit = 10000 * readmission_rate

        low_cost = car_t_drug_cost + facility[0] + staffing[0] + services[0] + readmit
        high_cost = car_t_drug_cost + facility[1] + staffing[1] + services[1] + readmit

        return (
            round(inpatient_reimbursement - high_cost, 2),
            round(inpatient_reimbursement - low_cost, 2)
        )

    inpatient_margin_low, inpatient_margin_high = margin_range()
    inpatient_margin_avg = (inpatient_margin_low + inpatient_margin_high) / 2

    shifted = patient_volume * (outpatient_shift_pct / 100)
    remaining = patient_volume - shifted

    # Anchor against average inpatient margin baseline
    baseline = inpatient_margin_avg * patient_volume

    new_low = (inpatient_margin_low * remaining) + (amortized_outpatient_margin * shifted)
    new_high = (inpatient_margin_high * remaining) + (amortized_outpatient_margin * shifted)

    improvement_low = new_low - baseline
    improvement_high = new_high - baseline

    return improvement_low, improvement_high, shifted, patient_volume

# --- UI ---
st.set_page_config(page_title="CAR-T Financial Calculator", page_icon="🧬", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #E0E6EF;
    }
    h1, h2, h3 {
        color: #5842ff;
    }
    .stButton button {
        background-color: #ff4861;
        color: white;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #110854;
    }
    </style>
""", unsafe_allow_html=True)

st.image("CH_Primary.svg", width=160)
st.title("CAR-T Episode Financial Impact Calculator")

st.markdown("Use this tool to estimate the **annual margin improvement range** when shifting patients to outpatient CAR-T care.")

medicare_pct = st.slider("Payer Mix: Percent Medicare", 0, 100, 50)
los = st.slider("Inpatient Length of Stay (days)", 5, 20, 10)
readmit_rate = st.slider("Readmission Rate", 0.0, 0.5, 0.15, step=0.01)
volume = st.number_input("Annual Patient Volume", min_value=1, value=500)
shift = st.slider("% of Volume Shifted to Outpatient", 0, 100, 75, step=5)

if st.button("Calculate Impact"):
    low, high, shifted_patients, total_volume = car_t_financial_model(medicare_pct, los, readmit_rate, volume, shift)

    st.markdown("### 💰 Estimated Annual Financial Improvement")
    st.markdown(f"""
    <div style='font-size: 36px; font-weight: bold; color: #5842ff;'>
      ${low:,.0f} to ${high:,.0f}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"Based on shifting **{int(shifted_patients)}** of **{total_volume}** patients to outpatient care.")
    st.markdown("Includes amortized $75,000 implementation fee and updated inpatient cost realism.")
