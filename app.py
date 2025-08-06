from typing import Literal
import streamlit as st

def car_t_financial_model(
    payer_type: Literal['Medicare', 'Commercial'] = 'Medicare',
    ntap_applies: bool = True,
    inpatient_los_days: int = 10,
    readmission_rate: float = 0.15
):
    car_t_drug_cost = 373000

    reimbursement = {
        'Medicare': {
            'Inpatient': 450000 + (50000 if ntap_applies else 0),
            'Outpatient': 430000
        },
        'Commercial': {
            'Inpatient': 550000 + (50000 if ntap_applies else 0),
            'Outpatient': 500000
        }
    }

    facility_cost_per_day = {
        'Inpatient': 7500,
        'Outpatient': 3000
    }

    staffing_cost = {
        'Inpatient': 20000,
        'Outpatient': 10000
    }

    monitoring_followup = {
        'Inpatient': 10000,
        'Outpatient': 15000
    }

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

    inpatient_margin = reimbursement[payer_type]['Inpatient'] - inpatient_total_cost
    outpatient_margin = reimbursement[payer_type]['Outpatient'] - outpatient_total_cost

    return {
        'Scenario': f"{payer_type} | NTAP: {'Yes' if ntap_applies else 'No'} | LOS: {inpatient_los_days} days",
        'Inpatient Total Cost': round(inpatient_total_cost, 2),
        'Outpatient Total Cost': round(outpatient_total_cost, 2),
        'Inpatient Reimbursement': reimbursement[payer_type]['Inpatient'],
        'Outpatient Reimbursement': reimbursement[payer_type]['Outpatient'],
        'Inpatient Margin': round(inpatient_margin, 2),
        'Outpatient Margin': round(outpatient_margin, 2),
        'Net Improvement (Outpatient vs Inpatient)': round(outpatient_margin - inpatient_margin, 2)
    }

# Streamlit Interface
st.title("CAR-T Episode Financial Impact Calculator")

payer = st.selectbox("Select Payer Type", ["Medicare", "Commercial"])
ntap = st.checkbox("NTAP Applies?", value=True)
los = st.slider("Inpatient Length of Stay (days)", 5, 20, 10)
readmit_rate = st.slider("Readmission Rate", 0.0, 0.5, 0.15, step=0.01)

if st.button("Calculate"):
    results = car_t_financial_model(payer, ntap, los, readmit_rate)
    st.subheader("Results")
    for key, value in results.items():
        st.write(f"**{key}:** ${value:,.2f}" if isinstance(value, (int, float)) else f"**{key}:** {value}")
