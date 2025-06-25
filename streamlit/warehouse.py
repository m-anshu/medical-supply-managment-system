import streamlit as st
from addWarehouse import add_warehouse  # Import the add warehouse function
from viewInventory import view_inventory  # Import the view inventory function
from removeWarehouse import remove_warehouse
# Function to display the warehouse dashboard options
def warehouse_dashboard():
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose an option:", ("Add Warehouse", "View Inventory","Remove Warehouse"))

    # Redirect to the selected page based on the sidebar choice
    if choice == "Add Warehouse":
        add_warehouse()  # Show add warehouse page
    elif choice == "View Inventory":
        view_inventory()  # Show view inventory page
    elif choice == "Remove Warehouse":
        remove_warehouse()
