import streamlit as st
from supplier_stats import supplier_stats  # Assumes a supplier_stats() function is defined in supplier_stats.py
from client_stats import client_stats      # Assumes a client_stats() function is defined in client_stats.py

def stats_page():
    st.title("Statistics Dashboard")

    # Sidebar for navigating between Supplier and Client stats
    st.sidebar.header("Select Stats Type")
    stats_option = st.sidebar.radio("View Stats For:", ("Supplier", "Client"))

    # Display the selected stats page
    if stats_option == "Supplier":
        st.subheader("Supplier Statistics")
        supplier_stats()
    elif stats_option == "Client":
        st.subheader("Client Statistics")
        client_stats()
