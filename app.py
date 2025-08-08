from typing import Tuple
import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter

# --- CONFIGURATION ---
OUTPATIENT_COST_PER_PATIENT = 450 * 15 + 15000  # $6,750 for 15 days + $15,000 additional cost
IMPLEMENTATION_FEE = 75000

INPATIENT_MARGIN_LOW = -33000
INPATIENT_MARGIN_MID = -20000

# --- MAIN CALCULATOR FUNCTION ---
def calculate_impact(medicare_mix: int, volume: int, shift_pct: int) -> Tuple[int, int]:
    outpatient_margin = 373000 - OUTPATIENT_COST_PER_PATIENT
    shifted = round(volume * shift_pct / 100)
    not_shifted = volume - shifted
    outpatient_total_margin = (outpatient_margin * shifted) - IMPLEMENTATION_FEE

    inpatient_margin_low = (
    payer_mix * inpatient_medicare_low +
    commercial_mix * inpatient_commercial_low
)

    inpatient_margin_mid = (
    payer_mix * inpatient_medicare_mid +
    commercial_mix * inpatient_commercial_mid
)


    impact_low = (outpatient_margin - inpatient_margin_mid) * patients_shifted
    impact_high = (outpatient_margin - inpatient_margin_low) * patients_shifted


    return round(impact_low), round(impact_mid)

# --- STREAMLIT UI ---
st.set_page_config(page_title="CAR-T Estimator", layout="centered")
st.image("CH_Primary.png", width=160)
st.title("CAR-T Care Episode Financial Impact Estimator")

medicare_mix = st.slider("Medicare Payer Mix (%)", 0, 100, 50)
volume = st.number_input("Annual CAR-T Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent of Volume Shifted to Outpatient", 0, 100, 75)

if st.button("See Impact"):
    impact_low, impact_mid = calculate_impact(medicare_mix, volume, shift_pct)
    st.markdown("### Your Estimated Financial Impact with Current Health:")
    st.markdown(f"<h2 style='color:#5842ff;'>${impact_low:,} - ${impact_mid:,}</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: gray;'>Range reflects shifting patients from a typical inpatient model to Current Health's outpatient episode.</p>", unsafe_allow_html=True)

    # --- DOWNLOAD PDF BUTTON ---
    if st.button("Download My Estimate"):
        template_path = "CAR-T_calculator_output3.pdf"
        reader = PdfReader(template_path)
        writer = PdfWriter()
        writer.append(reader.pages[0])

        # Fill in the fields (update with actual field names in the PDF)
        writer.update_page_form_field_values(
            writer.pages[0],
            {
                "payer_mix": f"{medicare_mix}%",
                "volume": str(volume),
                "shifted": f"{round(volume * shift_pct / 100)}",
                "range": f"${impact_low:,} - ${impact_mid:,}",
            },
        )
        output_pdf = BytesIO()
        writer.write(output_pdf)
        st.download_button(
            label="Download My Estimate",
            data=output_pdf.getvalue(),
            file_name="CAR-T_Impact_Estimate.pdf",
            mime="application/pdf",
        )
