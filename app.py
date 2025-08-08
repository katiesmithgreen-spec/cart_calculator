import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

# --- CONFIGURATION ---
DRUG_COST = 373000
MEDICARE_REIMBURSEMENT_INPATIENT = 498723
MEDICARE_REIMBURSEMENT_OUTPATIENT = 414393

# Calculate non-drug reimbursements
NONDRUG_REIMBURSEMENT_INPATIENT = MEDICARE_REIMBURSEMENT_INPATIENT - DRUG_COST
NONDRUG_REIMBURSEMENT_OUTPATIENT = MEDICARE_REIMBURSEMENT_OUTPATIENT - DRUG_COST

# Outpatient cost structure
OUTPATIENT_COST = 450 * 15 + 15000  # Monitoring + facilities/staff
IMPLEMENTATION_FEE = 75000

# Inpatient margin assumptions
INPATIENT_MARGIN_LOW = -40000
INPATIENT_MARGIN_MID = -10000

def calculate_impact(volume: int, shift_pct: int):
    patients_shifted = round(volume * shift_pct / 100)

    outpatient_margin = NONDRUG_REIMBURSEMENT_OUTPATIENT - OUTPATIENT_COST

    delta_low = outpatient_margin - INPATIENT_MARGIN_MID
    delta_high = outpatient_margin - INPATIENT_MARGIN_LOW

    impact_low = round(delta_low * patients_shifted - IMPLEMENTATION_FEE)
    impact_high = round(delta_high * patients_shifted - IMPLEMENTATION_FEE)

    return impact_low, impact_high, patients_shifted

# --- STREAMLIT UI ---
st.set_page_config(page_title="CAR-T Estimator", layout="centered")
st.image("CH_Primary.png", width=160)
st.title("CAR-T Care Episode Financial Impact Estimator")

volume = st.number_input("Annual CAR-T Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent of Volume Shifted to Outpatient", 0, 100, 75)

if st.button("See Impact"):
    impact_low, impact_high, shifted = calculate_impact(volume, shift_pct)
    st.markdown("### Your Estimated Financial Impact with Current Health:")
    st.markdown(
        f"<h2 style='color:#5842ff;'>${impact_low:,} - ${impact_high:,}</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color: gray;'>Range reflects shifting patients from a typical inpatient model to Current Health's outpatient episode.</p>",
        unsafe_allow_html=True
    )

    if st.button("Download My Estimate"):
        reader = PdfReader("CAR-T_calculator_output3.pdf")
        writer = PdfWriter()
        writer.append(reader.pages[0])

        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "payer_mix": "Medicare only",
                "volume": str(volume),
                "shifted": str(shifted),
                "range": f"${impact_low:,} - ${impact_high:,}",
            }
        )

        output_pdf = BytesIO()
        writer.write(output_pdf)
        st.download_button(
            label="⬇️ Download My Estimate",
            data=output_pdf.getvalue(),
            file_name="CAR-T_Impact_Estimate.pdf",
            mime="application/pdf"
        )
