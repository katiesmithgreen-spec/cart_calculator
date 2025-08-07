
from typing import Literal
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from PIL import Image

# --- CAR-T Financial Model ---
def car_t_financial_model(
    medicare_pct: int = 50,
    inpatient_los_days: int = 10,
    readmission_rate: float = 0.15
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

    # OUTPATIENT model
    outpatient_current_health_cost = 450 * 15  # daily x 15 days
    outpatient_monitoring_fixed = 75000  # one-time implementation fee
    outpatient_other_fixed = 15000  # labs, scans, infusion services

    outpatient_total_cost = (
        car_t_drug_cost + outpatient_current_health_cost + outpatient_other_fixed
    )
    # Per patient cost for outpatient (amortizing fixed CH fee across volume will happen later)
    outpatient_margin = outpatient_reimbursement - outpatient_total_cost

    # INPATIENT ranges (returns low, mid, high cost versions)
    def inpatient_cost_range(los):
        # Facility: $10K–$25K for typical stays
        facility_cost_low = 10000
        facility_cost_high = 25000

        # Staffing: $15K–$35K
        staffing_cost_low = 15000
        staffing_cost_high = 35000

        # Services: $6K–$20K
        services_low = 6000
        services_high = 20000

        readmit = 10000 * readmission_rate

        low_total = car_t_drug_cost + facility_cost_low + staffing_cost_low + services_low + readmit
        high_total = car_t_drug_cost + facility_cost_high + staffing_cost_high + services_high + readmit

        low_margin = inpatient_reimbursement - low_total
        high_margin = inpatient_reimbursement - high_total
        return (round(low_margin, 2), round(high_margin, 2))

    inpatient_margin_low, inpatient_margin_high = inpatient_cost_range(inpatient_los_days)

    return {
        'Inpatient Margin Range': (inpatient_margin_low, inpatient_margin_high),
        'Outpatient Margin': round(outpatient_margin, 2)
    }

# --- Streamlit UI ---
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
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.image("CH_Primary.svg", width=160)

st.title("CAR-T Episode Financial Impact Calculator")
st.markdown("Use this tool to model the potential margin improvement of outpatient care delivery for CAR-T.")

# Payer mix slider (Medicare %)
st.markdown("**Payer Mix**")
medicare_pct = st.slider("Percent Medicare Patients", 0, 100, 50)
st.markdown(f"💰 **Payer Mix Breakdown:** {medicare_pct}% Medicare &nbsp;&nbsp;|&nbsp;&nbsp; {100 - medicare_pct}% Commercial")

los = st.slider("Inpatient Length of Stay (days)", 5, 20, 10)
readmit_rate = st.slider("Readmission Rate", 0.0, 0.5, 0.15, step=0.01)

st.markdown("### 📈 Volume-Based Impact Modeling")
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500, step=1)
outpatient_shift_pct = st.slider("% of Volume Shifted to Outpatient", 0, 100, 75, step=5)

if st.button("Calculate"):
    results = car_t_financial_model(medicare_pct, los, readmit_rate)

    st.subheader("📊 Per-Patient Margins")
    inpatient_low, inpatient_high = results['Inpatient Margin Range']
    outpatient_margin = results['Outpatient Margin']

    st.write(f"**Inpatient Margin Range:** ${inpatient_low:,.2f} to ${inpatient_high:,.2f}")
    st.write(f"**Outpatient Margin (excludes implementation fee):** ${outpatient_margin:,.2f}")

    # Adjust outpatient margin by amortizing implementation fee across patients
    implementation_fee = 75000
    amortized_per_patient = implementation_fee / patient_volume
    adj_outpatient_margin = outpatient_margin - amortized_per_patient

    # Scenario volume math
    shifted_patients = patient_volume * (outpatient_shift_pct / 100)
    inpatient_patients = patient_volume - shifted_patients

    baseline_low = inpatient_low * patient_volume
    baseline_high = inpatient_high * patient_volume
    new_low = (inpatient_low * inpatient_patients) + (adj_outpatient_margin * shifted_patients)
    new_high = (inpatient_high * inpatient_patients) + (adj_outpatient_margin * shifted_patients)

    st.markdown("---")
    st.subheader("📈 Volume-Adjusted Financial Impact")
    st.write(f"**Annual Volume:** {patient_volume} patients")
    st.write(f"**Patients Shifted to Outpatient:** {int(shifted_patients)} ({outpatient_shift_pct}%)")
    st.write(f"**Estimated Annual Margin Improvement Range:** ${new_low - baseline_low:,.0f} to ${new_high - baseline_high:,.0f}")

    fig, ax = plt.subplots(figsize=(6, 5))
    labels = ["All Inpatient (Low)", "All Inpatient (High)", "With Outpatient Shift (Low)", "With Outpatient Shift (High)"]
    values = [baseline_low, baseline_high, new_low, new_high]
    colors = ['#ccc', '#999', '#a6c8ff', '#5842ff']
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Total Annual Margin ($)", fontsize=12)
    ax.set_title("Estimated Total Annual Margin Improvement", fontsize=14)
    ax.set_ylim(0, max(values) * 1.25)

    for i, v in enumerate(values):
        ax.text(i, v + (0.03 * max(values)), f"${v:,.0f}", ha='center', va='bottom', fontsize=10)

    st.pyplot(fig)
    st.success("Updated model generated successfully!")
