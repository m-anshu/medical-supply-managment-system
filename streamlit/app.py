import streamlit as st
from login import login_page
from client_dashboard import client_dashboard  # Import the order page
from addMedicine import add_medicine_page  # Import the add medicine page
from supplier_dashboard import supplier_dashboard
from employee_dashboard import employee_dashboard
# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None  # Store the username

# Function to handle logout
def logout():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None

def main():
    # Show logout button if user is logged in
    if st.session_state['logged_in']:
        # Create a logout button in the sidebar
        st.sidebar.button("Logout", on_click=logout, key="logout_button")

        # Redirect user to the appropriate dashboard based on their role
        if st.session_state['role'] == "Client":
            client_dashboard()  # Redirect to the order page for clients
        elif st.session_state['role'] == "Supplier":
            supplier_dashboard()  # Redirect to the add medicine page for suppliers
        elif st.session_state['role'] == "Employee":
            employee_dashboard()
        else:
            st.write("Access Denied: You do not have the necessary permissions.")
    else:
        # Pass unique key to login_page elements if any selectboxes or inputs are used there
        login_page()

if __name__ == "__main__":
    main()
