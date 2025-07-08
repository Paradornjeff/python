import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import gspread
from google.oauth2.service_account import Credentials

def append_to_gsheet(gender, age, activity):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = st.secrets["google_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    sheet = client.open("park_survey_data").sheet1
    sheet.append_row([gender, age, activity])

# # ---------- Google Sheets Function ----------
# def append_to_gsheet(gender, age, activity):
#     scope = [
#         "https://spreadsheets.google.com/feeds",
#         "https://www.googleapis.com/auth/drive"
#     ]
#     creds_dict = st.secrets["google_service_account"]
#     creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
#     client = gspread.authorize(creds)
#     sheet = client.open("park_survey_data").sheet1
#     sheet.append_row([gender, age, activity])


# ---------- App Configuration ----------
st.set_page_config(page_title="Public Park Survey", layout="centered")

st.title("🌳 Shma Public Park Survey Ver1.0")

activity_options = [
    "Walking",
    "Running",
    "Picnic/Relaxing",
    "Playing with Pets",
    "Photography/Drawing",
    "Sports (e.g. Football, Basketball)",
    "Reading",
    "Playing with Kids"
]

gender_options = {
    "Male": "Male",
    "Female": "Female",
    "Other": "Other"
}

# ---------- Session Data ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Gender", "Age", "Activity"])

# ---------- Input Form ----------
with st.form("survey_form"):
    st.subheader("📝 Fill out the survey")
    gender = st.selectbox("Select your gender:", list(gender_options.values()))
    age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)
    activity = st.selectbox("Select your activity:", activity_options)
    submitted = st.form_submit_button("Submit")

    if submitted:
        new_entry = {"Gender": gender, "Age": age, "Activity": activity}
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        append_to_gsheet(gender, age, activity)
        st.success("✅ Your response has been recorded!")

# ---------- Data Display ----------
if not st.session_state.data.empty:
    st.subheader("📋 All Survey Responses")
    st.dataframe(st.session_state.data)

    st.subheader("📊 Activity Summary")
    summary = st.session_state.data["Activity"].value_counts(normalize=True) * 100
    st.write(summary.round(2).astype(str) + " %")

    fig, ax = plt.subplots()
    summary.plot(kind='bar', ax=ax, color='mediumseagreen')
    ax.set_title("Activity Proportion (%)")
    ax.set_ylabel("Percentage")
    ax.set_xlabel("Activity")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # ---------- Additional Visualizations ----------
    df = st.session_state.data.copy()

    def age_group(age):
        if age <= 18:
            return "0-18"
        elif age <= 35:
            return "19-35"
        elif age <= 60:
            return "36-60"
        else:
            return "60+"

    df["Age Group"] = df["Age"].apply(age_group)

    st.subheader("📈 Insights for Landscape Designers")

    st.write("### Age Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["Age"], bins=10, kde=True, color="skyblue", ax=ax)
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    st.write("### Activity by Gender")
    fig, ax = plt.subplots(figsize=(10, 5))
    pd.crosstab(df["Activity"], df["Gender"], normalize='index').mul(100).plot(kind='bar', ax=ax, colormap='Set2')
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Activity")
    ax.legend(title="Gender")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    st.write("### Activity by Age Group")
    fig, ax = plt.subplots(figsize=(10, 5))
    pd.crosstab(df["Activity"], df["Age Group"], normalize='index').mul(100).plot(kind='bar', ax=ax, colormap='Pastel1')
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Activity")
    ax.legend(title="Age Group")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    st.write("### Gender Distribution")
    fig, ax = plt.subplots()
    df["Gender"].value_counts().plot.pie(
        autopct='%1.1f%%', startangle=90,
        colors=['#66b3ff', '#ff9999', '#99ff99'], ax=ax
    )
    ax.set_ylabel("")
    ax.set_title("Gender Proportion")
    st.pyplot(fig)
else:
    st.info("No data submitted yet.")
