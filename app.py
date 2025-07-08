import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# เชื่อม Google Sheets
def append_to_gsheet(gender, age, activity):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_key.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("park_survey_data").sheet1  # ชื่อ Sheet
    sheet.append_row([gender, age, activity])
# Activity and Gender options
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

# Initialize data storage
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Gender", "Age", "Activity"])

# App title
st.title("🌳Shma Public Park Survey Ver1.0")

# Form input
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
        st.success("✅ Your response has been recorded!")

    # 🔄 Append to Google Sheet instead of CSV
        append_to_gsheet(gender, age, activity)

    # if submitted:
    #     new_entry = {"Gender": gender, "Age": age, "Activity": activity}
    #     st.session_state.data = pd.concat(
    #         [st.session_state.data, pd.DataFrame([new_entry])],
    #         ignore_index=True
    #     )
    #     st.success("✅ Your response has been recorded!")
    #     print(st.session_state.data)
    #     # ✅ Save to CSV file
    #     #st.session_state.data.to_csv("park_survey_data.csv", index=False)
    #     with open('park_survey_data.csv', 'a', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow([gender, age, activity])

# Show all data
if not st.session_state.data.empty:
    st.subheader("📋 All Survey Responses")
    st.dataframe(st.session_state.data)

    # Summary chart
    st.subheader("📊 Activity Summary")
    summary = st.session_state.data["Activity"].value_counts(normalize=True) * 100
    st.write(summary.round(2).astype(str) + " %")

    # Plotting Activity Summary
    fig, ax = plt.subplots()
    summary.plot(kind='bar', ax=ax, color='mediumseagreen')
    ax.set_title("Activity Proportion (%)")
    ax.set_ylabel("Percentage")
    ax.set_xlabel("Activity")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # ========== Additional Visualizations for Landscape Designer ==========
    df = st.session_state.data.copy()

    # Helper function: categorize age groups
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

    st.subheader("📈 Additional Visualizations for Landscape Design")

    # 1. Age Distribution Histogram
    st.write("### Age Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df["Age"], bins=10, kde=True, color="skyblue", ax=ax)
    ax.set_xlabel("Age")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # 2. Activity by Gender (Grouped Bar Chart)
    st.write("### Activity by Gender")
    fig, ax = plt.subplots(figsize=(10, 5))
    activity_gender = pd.crosstab(df["Activity"], df["Gender"], normalize='index') * 100
    activity_gender.plot(kind='bar', stacked=False, ax=ax, colormap='Set2')
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Activity")
    ax.legend(title="Gender")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # 3. Activity by Age Group (Grouped Bar Chart)
    st.write("### Activity by Age Group")
    fig, ax = plt.subplots(figsize=(10, 5))
    activity_agegroup = pd.crosstab(df["Activity"], df["Age Group"], normalize='index') * 100
    activity_agegroup.plot(kind='bar', stacked=False, ax=ax, colormap='Pastel1')
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Activity")
    ax.legend(title="Age Group")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # 4. Gender Distribution Pie Chart
    st.write("### Gender Distribution")
    fig, ax = plt.subplots()
    df["Gender"].value_counts().plot.pie(
        autopct='%1.1f%%', startangle=90,
        colors=['#66b3ff','#ff9999','#99ff99'], ax=ax
    )
    ax.set_ylabel("")
    ax.set_title("Gender Proportion")
    st.pyplot(fig)
else:
    st.info("No data submitted yet.")
