import streamlit as st
from order import order_page
from order_history import order_history_page  # Uncomment to include the order history page

# Function to display client dashboard options
def client_dashboard():
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Choose an option:", ("Order Medicines", "View Order History"))

    # Redirect to the selected page based on the sidebar choice
    if choice == "Order Medicines":
        order_page()  # Show order page
    elif choice == "View Order History":
        # Ensure username is available in session state
        if 'username' in st.session_state:
            order_history_page(st.session_state.username)  # Pass logged-in username
        else:
            st.error("Please log in to view order history.")
