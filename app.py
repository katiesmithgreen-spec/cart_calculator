
import streamlit as st
import datetime
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

# Title and logo
st.image("CH_Primary.png", width=160)
st.title("CAR-T Episode Financial Impact Calculator")

# Input controls
payer_mix = st.slider("Payer Mix (% Medicare)", 0, 100, 62)
patient_volume = st.number_input("Annual Patient Volume", min_value=1, value=500)
shift_pct = st.slider("Percent Shifted to Outpatient", 0, 100, 75)

# Financial impact range (normally calculated)
impact_low = 2100000
impact_high = 6700000

if st.button("Download Personalized Estimate PDF"):
    # Load PDF template
    template = "CAR-T_calculator_output3.pdf"
    reader = PdfReader(template)
    writer = PdfWriter()

    # Placeholder map
    placeholder_map = {
        "{{PAYER_MIX}}": f"{payer_mix}% Medicare",
        "{{PATIENT_VOLUME}}": str(patient_volume),
        "{{OUTPATIENT_SHIFT}}": f"{round(patient_volume * shift_pct / 100)} ({shift_pct}%)",
        "{{IMPACT_RANGE}}": f"${impact_low:,} to ${impact_high:,}"
    }

    # Copy pages to writer (text replacement not supported in PyPDF2 — placeholders are just visual)
    for page in reader.pages:
        writer.add_page(page)

    # Output to BytesIO
    output_stream = BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)

    st.download_button(
        label="📄 Download My Estimate",
        data=output_stream,
        file_name="Your_CART_Impact_Estimate.pdf",
        mime="application/pdf"
    )
