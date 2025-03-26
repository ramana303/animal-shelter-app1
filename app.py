import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ---- GOOGLE SHEETS SETUP ----
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "animal-shelter-streamlit-f79e45197ef2.json"  # <- Your downloaded JSON key file
SPREADSHEET_NAME = "Animal_Shelter_Data"

def connect_to_gsheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    return sheet

# ---- LOGIN SYSTEM (hardcoded for simplicity) ----
USER_CREDENTIALS = {"admin": "1234", "user": "abcd"}

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Invalid username or password")

# ---- VIEW DATA ----
def view_animals(sheet):
    st.subheader("Current Animals in Shelter")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if not df.empty:
        st.dataframe(df)
    else:
        st.write("No animals in the shelter yet!")

# ---- ADD ANIMAL ----
def add_animal(sheet):
    st.subheader("Add New Animal")
    animal = st.text_input("Animal Name")
    age = st.number_input("Age", min_value=0, step=1)
    status = st.text_input("Status (domestic/stray)")
    species = st.text_input("Species")

    if st.button("Add Animal"):
        if animal and age and status and species:
            current_data = sheet.get_all_records()
            next_id = len(current_data) + 1
            sheet.append_row([next_id, animal, age, status, species])
            st.success(f"Added {animal} to shelter!")
        else:
            st.error("Please fill all fields!")

# ---- ADOPT ANIMAL ----
def adopt_animal(sheet):
    st.subheader("Adopt (Remove) Animal")
    adopt_id = st.number_input("Enter Animal ID to adopt", min_value=1, step=1)

    if st.button("Adopt"):
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if adopt_id <= len(df):
            sheet.delete_rows(adopt_id + 1)  # +1 for header row
            st.success(f"Animal with ID {adopt_id} adopted!")
        else:
            st.error("Invalid Animal ID")

# ---- MAIN APP ----
def main_app():
    sheet = connect_to_gsheet()
    
    st.title("🐾 Animal Shelter Management Dashboard")
    st.sidebar.title("Menu")

    menu = st.sidebar.radio("Select Action", ["View Animals", "Add Animal", "Adopt Animal"])

    if menu == "View Animals":
        view_animals(sheet)
    elif menu == "Add Animal":
        add_animal(sheet)
    elif menu == "Adopt Animal":
        adopt_animal(sheet)

# ---- APP START ----
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    main_app()
