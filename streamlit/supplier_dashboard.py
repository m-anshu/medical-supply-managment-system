import streamlit as st
from addMedicine import add_medicine_page
from add_history import supply_history_page  # Uncomment to include the order history page

# Function to display client dashboard options
def supplier_dashboard():
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose an option:", ("Add Medicines", "View History"))

    # Redirect to the selected page based on the sidebar choice
    if choice == "Add Medicines":
        add_medicine_page()  # Show order page
    elif choice == "View History":
        # Ensure username is available in session state
        if 'username' in st.session_state:
            supply_history_page(st.session_state.username)  # Pass logged-in username
        else:
            st.error("Please log in to view order history.")