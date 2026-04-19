import streamlit as st
import requests

st.set_page_config(page_title="Medical Report Generator", page_icon="🏥")

st.title("🏥 GenAI Medical Report Generator")
st.write("Enter patient details and generate a report.")

# Inputs
name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=1, max_value=120, step=1)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])

bp = st.text_input("Blood Pressure", "120/80")
temp = st.text_input("Temperature", "98.6F")
hr = st.text_input("Heart Rate", "72")

complaints = st.text_area("Chief Complaint")
history = st.text_area("Medical History")

# Button
if st.button("Generate Report"):

    data = {
        "name": name,
        "age": age,
        "gender": gender,
        "vitals": {
            "BP": bp,
            "Temp": temp,
            "HR": hr
        },
        "complaints": complaints,
        "medical_history": history
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/generate-report",
            json=data
        )

        if response.status_code == 200:
            result = response.json()

            st.success("Report Generated Successfully!")

            st.subheader("📄 Structured Report")
            st.text(result["structured_report"])

            st.subheader("🩺 ICD-10 Suggestions")
            for item in result["icd10_suggestions"]:
                st.write("-", item)

            st.subheader("⚠ Disclaimer")
            st.info(result["disclaimer"])

        else:
            st.error("Failed to generate report.")

    except:
        st.error("Backend server not running. Start main.py first.")