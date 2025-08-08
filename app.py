from typing import Tuple
import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

# --- CONFIGURATION ---
OUTPATIENT_COST_PER_PATIENT = 450 * 15 + 15000  # $6,750 for 15 days + $15,000 additional cost
IMPLEMENTATION_FEE = 75000
CAR_T_REIMBURSEMENT = 373000

# Inpatient margin assumptions
inpatient_medicare_low = -40000
inpatient_medicare_mid = -30000
inpatient_commercial_low = -25000
inpatient_commercial_mid = -15000

# --- CALCULATION FUNCTION ---
def calculate_impact(medicare_mix: int, volume: int, shift_pct: int) -> Tuple[int, int]:
    medicare_ratio = medicare_mix / 100
    commercial_ratio = 1 - medicare_ratio
    patients_shifted = round(volume * shift_pct / 100)

    outpatient_cost = OUTPATIENT_COST_PER_PATIENT
    outpatient_margin = CAR_T_REIMBURSEMENT - outpatient_cost

    # Weighted inpatient margins
    inpatient_margin_low = (
        medicare_ratio * inpatient_medicare_low +
        commercial_ratio * inpatient_commercial_low
    )
    inpatient_margin_mid = (
        medicare_ratio * inpatient_medicare_mid +
        commercial_ratio * inpatient_commercial_mid
    )

    # Margin delta per patient
    delta_low = outpatient_margin - inpatient_margin_mid
    delta_high = outpatient_margin - inpatient_margin_low

    impact_low = round(delta_low * patients_shifted - IMPLEMENTATION_FEE)
    impact_high = round(delta_high * patients_shifted - IMPLEMENTATION_FEE)

    return impact_low, impact_high, patients_shifted

# --- STREAMLIT UI ---
st.set_page_config(page_title="CAR-T Estimator", layout="centered")
st.image("CH_Primary.png", width=160)
st.title("CAR-T Care Episode Financial Impact Estimator")

medicare_mix = st.slider("Medicare Payer Mix (%)", 0, 100, 50)
volume = st.number_input("Annual CAR-T Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent of Volume Shifted to Outpatient", 0, 100, 75)

if st.button("See Impact"):
    impact_low, impact_high, shifted = calculate_impact(medicare_mix, volume, shift_pct)
    st.markdown("### Your Estimated Financial Impact with Current Health:")
    st.markdown(
        f"<h2 style='color:#5842ff;'>${impact_low:,} - ${impact_high:,}</h2>",
        unsafe_allow_html=True
    )
    st.markdown("<p style='color: gray;'>Range reflects shifting patients from a typical inpatient model to Current Health's outpatient episode.</p>", unsafe_allow_html=True)

    if st.button("Download My Estimate"):
        reader = PdfReader("CAR-T_calculator_output3.pdf")
        writer = PdfWriter()
        writer.append(reader.pages[0])

        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "payer_mix": f"{medicare_mix}%",
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
