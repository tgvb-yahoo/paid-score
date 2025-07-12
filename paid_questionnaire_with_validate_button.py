
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="PAID Diabetes Questionnaire", layout="wide")

# -- Enumerators and Admin credentials --
USER_CREDENTIALS = {f"enum{str(i).zfill(2)}": f"pass{str(i).zfill(2)}" for i in range(1, 26)}
USER_CREDENTIALS["admin"] = "admin123"

# -- Initialize Session State --
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if "validated" not in st.session_state:
    st.session_state.validated = False

# -- Logout Button --
def logout_button():
    st.sidebar.markdown("## ⚙️ Settings")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.validated = False
        st.success("You have been logged out.")

# -- Login Page --
def login_page():
    st.title("Login: PAID Questionnaire System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid credentials.")

# -- Admin Dashboard --
def admin_dashboard():
    st.title("🗂️ Admin Dashboard: PAID Questionnaire Data")
    file_path = "paid_questionnaire_new_data.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        st.dataframe(df)
        st.download_button("📥 Download Data as CSV", df.to_csv(index=False), file_name="paid_data.csv")
    else:
        st.warning("No data available yet.")

# -- Questionnaire Form --
def questionnaire_page():
    st.title("🩺 PAID Questionnaire for Diabetes Distress")
    st.caption(f"Logged in as: {st.session_state.username}")

    st.header("Patient Information")
    patient_id = st.text_input("Patient ID", max_chars=20)
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=1, max_value=120)
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    profession = st.selectbox("Occupation", ["Select", "Student", "Corporate Sector", "Govt Sector", "Business", "Self-employed"])
    income_pct = st.slider("What percentage of your income goes to diabetes-related medicines?", 0, 100)
    follow_ups = st.number_input("How many follow-up visits did you have in the last 6 months?", min_value=0)
    retinopathy = st.radio("Do you have Diabetic Retinopathy?", ["Yes", "No"])

    st.divider()

    st.header("PAID Questionnaire")

    questions = [
        "Feeling scared when you think about living with diabetes",
        "Worrying about the future and possible serious complications",
        "Feeling overwhelmed by your diabetes regimen",
        "Feeling angry when you think about having diabetes",
        "Feeling depressed when you think about living with diabetes",
        "Coping with complications of diabetes",
        "Feeling alone with your diabetes",
        "Feeling that your friends and family are not supportive of your diabetes management",
        "Feeling that diabetes limits your social life",
        "Worrying about low blood sugar reactions",
        "Feeling discouraged with your diabetes treatment plan",
        "Feeling worried about future complications",
        "Not accepting your diabetes",
        "Feeling that diabetes is taking up too much of your mental and physical energy",
        "Feeling that you are not in control of your diabetes",
        "Worrying about your sexual life because of diabetes",
        "Feeling guilty when you get off track with your diabetes management",
        "Not feeling motivated to keep up your diabetes management",
        "Worrying about your job or studies being affected by diabetes",
        "Feeling burned out from having to manage diabetes"
    ]

    response_options = {
        "Not a problem (0)": 0,
        "Minor problem (1)": 1,
        "Moderate problem (2)": 2,
        "Somewhat serious problem (3)": 3,
        "Serious problem (4)": 4
    }

    responses = []
    for i, q in enumerate(questions):
        answer = st.radio(f"Q{i+1}: {q}", list(response_options.keys()), key=q)
        responses.append(response_options[answer])

    if st.button("✅ Validate Input"):
        if not all([patient_id.strip(), name.strip()]) or gender == "Select" or profession == "Select":
            st.session_state.validated = False
            st.warning("❗ Please complete all required patient fields before submission.")
        else:
            st.session_state.validated = True
            st.success("✅ All required fields are valid. You may now submit.")

    if st.session_state.validated:
        if st.button("📤 Submit & Calculate Score"):
            raw_score = sum(responses)
            paid_score = raw_score * 1.25

            if paid_score < 40:
                level = "Low Distress"
                color = "✅ "
            elif paid_score < 60:
                level = "Moderate Distress"
                color = "🟡"
            else:
                level = "High Distress"
                color = "🔴"

            st.success(f"Your PAID Score is **{paid_score:.2f} / 100**")
            st.markdown(f"### Result: {level} ({color})")

            data = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Enumerator": st.session_state.username,
                "Patient_ID": patient_id,
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Occupation": profession,
                "%_Income_on_Medicine": income_pct,
                "#_Follow_Up_Visits": follow_ups,
                "Diabetic_Retinopathy": retinopathy,
            }

            for i in range(20):
                data[f"Q{i+1}"] = responses[i]

            data["Raw_Score"] = raw_score
            data["PAID_Score"] = paid_score
            data["Distress_Level"] = level

            df = pd.DataFrame([data])
            file_path = "paid_questionnaire_new_data.csv"
            df.to_csv(file_path, mode="a", header=not os.path.exists(file_path), index=False)

            st.success("✅ Data saved successfully!")

            st.subheader("Score Summary")
            st.bar_chart(pd.DataFrame({
                "Score": [raw_score, paid_score],
            }, index=["Raw Score", "PAID Score"]))

# -- Main App Logic --
if not st.session_state.logged_in:
    login_page()
else:
    logout_button()
    if st.session_state.username.strip().lower() == "admin":
        admin_dashboard()
    else:
        questionnaire_page()
