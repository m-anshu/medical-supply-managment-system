import streamlit as st
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
# Function to create a database connection
def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# Supplier stats page
def supplier_stats():
    st.title("Supplier Statistics")
    
    # Step 1: Fetch all unique usernames from the supplier table
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM supplier")  # Fetch usernames from supplier table
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()

    # Check if there are any suppliers
    if not suppliers:
        st.write("No suppliers found.")
        return

    # Display a list of usernames in a dropdown
    usernames = [supplier[0] for supplier in suppliers]
    selected_username = st.selectbox("Select a Supplier Username", usernames)

    # Step 2: Fetch and display supply history for the selected username
    if selected_username:
        conn = create_connection()
        cursor = conn.cursor()

        # Fetch supplies by the selected supplier
        cursor.execute("""
            SELECT s.supply_id, s.supply_date, si.medicine_name, si.quantity
            FROM supply s
            JOIN supply_items si ON s.supply_id = si.supply_id
            WHERE s.username = %s
            ORDER BY s.supply_date DESC
        """, (selected_username,))

        supply_data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Check if there is any supply data
        if supply_data:
            # Convert the supply data into a DataFrame for display
            df = pd.DataFrame(supply_data, columns=["Supply ID", "Supply Date", "Medicine Name", "Quantity"])
            st.write(f"Supply History for '{selected_username}':")
            supply_counter = 1

            # Group by 'Supply ID' to display the data as requested
            for supply_id, group in df.groupby("Supply ID"):
                st.write(f"Supply ID: {supply_counter}")  # Display the counter instead of the actual Supply ID
                for _, row in group.iterrows():
                    st.write(f"- {row['Medicine Name']} (Quantity: {row['Quantity']})")
                supply_counter += 1  # Increment the counter for the next supply ID
        else:
            st.write(f"No supply history found for '{selected_username}'.")

# Run the supplier_stats function
if __name__ == "__main__":
    supplier_stats()
