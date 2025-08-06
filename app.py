
from typing import Literal
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Load logo
from PIL import Image

# --- CAR-T Financial Model ---
def car_t_financial_model(
    payer_mix: int = 50,
    ntap_applies: bool = True,
    inpatient_los_days: int = 10,
    readmission_rate: float = 0.15
):
    car_t_drug_cost = 373000

    reimbursement = {
        'Medicare': {'Inpatient': 450000 + (50000 if ntap_applies else 0), 'Outpatient': 430000},
        'Commercial': {'Inpatient': 550000 + (50000 if ntap_applies else 0), 'Outpatient': 500000}
    }

    inpatient_reimbursement = (
        (payer_mix / 100) * reimbursement['Commercial']['Inpatient'] +
        ((100 - payer_mix) / 100) * reimbursement['Medicare']['Inpatient']
    )
    outpatient_reimbursement = (
        (payer_mix / 100) * reimbursement['Commercial']['Outpatient'] +
        ((100 - payer_mix) / 100) * reimbursement['Medicare']['Outpatient']
    )

    facility_cost_per_day = {'Inpatient': 7500, 'Outpatient': 3000}
    staffing_cost = {'Inpatient': 20000, 'Outpatient': 10000}
    monitoring_followup = {'Inpatient': 10000, 'Outpatient': 15000}
    readmission_cost = {
        'Inpatient': 5000 * readmission_rate,
        'Outpatient': 15000 * readmission_rate
    }

    inpatient_facility_cost = inpatient_los_days * facility_cost_per_day['Inpatient']
    outpatient_facility_cost = 2 * facility_cost_per_day['Outpatient']

    inpatient_total_cost = (
        car_t_drug_cost + inpatient_facility_cost + staffing_cost['Inpatient'] +
        monitoring_followup['Inpatient'] + readmission_cost['Inpatient']
    )
    outpatient_total_cost = (
        car_t_drug_cost + outpatient_facility_cost + staffing_cost['Outpatient'] +
        monitoring_followup['Outpatient'] + readmission_cost['Outpatient']
    )

    inpatient_margin = inpatient_reimbursement - inpatient_total_cost
    outpatient_margin = outpatient_reimbursement - outpatient_total_cost

    return {
        'Inpatient Margin': round(inpatient_margin, 2),
        'Outpatient Margin': round(outpatient_margin, 2),
        'Net Improvement (Outpatient vs Inpatient)': round(outpatient_margin - inpatient_margin, 2)
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
st.markdown("Use this tool to compare inpatient vs outpatient margins for CAR-T therapy.")

payer_mix = st.slider("Payer Mix (% Commercial)", 0, 100, 50)
ntap = st.checkbox("NTAP Applies?", value=True)
los = st.slider("Inpatient Length of Stay (days)", 5, 20, 10)
readmit_rate = st.slider("Readmission Rate", 0.0, 0.5, 0.15, step=0.01)

st.markdown("### 📈 Volume-Based Impact Modeling")
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500, step=1)
outpatient_shift_pct = st.slider("% of Volume Shifted to Outpatient", 0, 100, 75, step=5)

if st.button("Calculate"):
    results = car_t_financial_model(payer_mix, ntap, los, readmit_rate)

    st.subheader("📊 Per-Patient Margins")
    for key, value in results.items():
        st.write(f"**{key}:** ${value:,.2f}")

    shifted_patients = patient_volume * (outpatient_shift_pct / 100)
    inpatient_patients = patient_volume - shifted_patients

    total_inpatient_margin = results['Inpatient Margin'] * inpatient_patients
    total_outpatient_margin = results['Outpatient Margin'] * shifted_patients

    baseline_total_margin = results['Inpatient Margin'] * patient_volume
    new_total_margin = total_inpatient_margin + total_outpatient_margin

    st.markdown("---")
    st.subheader("📈 Volume-Adjusted Financial Impact")
    st.write(f"**Annual Volume:** {patient_volume} patients")
    st.write(f"**Patients Shifted to Outpatient:** {int(shifted_patients)} ({outpatient_shift_pct}%)")
    st.write(f"**Estimated Total Net Financial Improvement:** ${new_total_margin - baseline_total_margin:,.2f}")

    # Chart
    fig, ax = plt.subplots()
    labels = ["All Inpatient", "Current Shift Model"]
    values = [baseline_total_margin, new_total_margin]
    colors = ['#ccc', '#5842ff']
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Total Margin ($)", fontsize=12)
    ax.set_title("Total Margin Impact: Inpatient vs Shift Model", fontsize=14)
    st.pyplot(fig)

    st.success("Calculation and volume comparison chart generated successfully!")
