import streamlit as st
from register import register_user_page  # Assuming you have a register_user.py file for registering users
from stats import stats_page  # Assuming you have a stats.py file for the stats page
from warehouse import warehouse_dashboard  # Assuming you have an inventory.py file for inventory management
from Medicines import medicines_dashboard # Assuming you have a low_quantity_medicines.py file
# Define the employee dashboard function
def employee_dashboard():
    st.sidebar.title("Employee Dashboard")

    # Sidebar navigation for employee-specific pages
    page = st.sidebar.radio("Select a page", ["Register New User", "Stats", "Warehouse", "Medicines Alerts"])

    # Show the appropriate page based on the sidebar selection
    if page == "Register New User":
        register_user_page()  # Redirect to the user registration page
    elif page == "Stats":
        stats_page()  # Redirect to the stats page
    elif page == "Warehouse":
        warehouse_dashboard()  # Redirect to the inventory management page
    elif page == "Medicines Alerts":
        medicines_dashboard()  # Redirect to the low quantity medicines page
