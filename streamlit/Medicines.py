import streamlit as st
from low_quantity_medicines import low_quantity_medicines_page  # Assuming low_quantity_medicines.py file exists
from expiring_medicines import expiring_medicines_page  # Assuming expiring_medicines.py file exists
from reqSupplier import req_supplier
# Define the medicines dashboard function
def medicines_dashboard():
    st.sidebar.title("Medicines Dashboard")

    # Sidebar navigation for sub-pages under "Medicines"
    page = st.sidebar.radio("Select a page", [
        "Low Medicines", 
        "Expiring Medicines"])

    # Show the appropriate page based on the sidebar selection
    if page == "Low Medicines":
        low_quantity_medicines_page()  # Page to display medicines with low stock
    elif page == "Expiring Medicines":
        expiring_medicines_page()  # Page to display medicines nearing expiry