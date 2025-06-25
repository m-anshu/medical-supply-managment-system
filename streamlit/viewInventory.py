import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import Error
import os
from dotenv import load_dotenv
# Function to connect to the MySQL database
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
    return connection

# Function to view inventory for a selected warehouse and calculate current capacity
def view_inventory():
    st.title("View Inventory")

    # Connect to the database
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Fetch all warehouses to populate the dropdown
        cursor.execute("SELECT warehouse_id, name, max_capacity FROM warehouse")
        warehouses = cursor.fetchall()

        # Create a dropdown for selecting a warehouse
        warehouse_options = {f"{name} (ID: {warehouse_id})": (warehouse_id, max_capacity) for warehouse_id, name, max_capacity in warehouses}
        selected_warehouse_info = st.selectbox("Select a Warehouse", list(warehouse_options.keys()))

        if st.button("Show Inventory"):
            # Get the selected warehouse ID and max capacity
            warehouse_id, max_capacity = warehouse_options[selected_warehouse_info]

            # Calculate current capacity (total quantity of medicines in the warehouse)
            cursor.execute("SELECT SUM(quantity) FROM medicines WHERE warehouse_id = %s", (warehouse_id,))
            current_capacity = cursor.fetchone()[0] or 0  # If no medicines, set current capacity to 0

            # Display warehouse capacity details
            st.write(f"**Warehouse Capacity Details for {selected_warehouse_info}:**")
            st.write(f"- **Max Capacity:** {max_capacity}")
            st.write(f"- **Current Capacity (Total Medicines):** {current_capacity}")

            # Fetch the inventory items for the selected warehouse
            cursor.execute("SELECT name, manufacture_date, expiry_date, quantity FROM medicines WHERE warehouse_id = %s", (warehouse_id,))
            inventory_items = cursor.fetchall()

            # Check if there are any items in the inventory
            if inventory_items:
                st.write(f"**Inventory for Warehouse ID {warehouse_id}:**")
                
                # Convert inventory items to a DataFrame for a scrollable table view
                df = pd.DataFrame(inventory_items, columns=["Name", "Manufacture Date", "Expiry Date", "Quantity"])
                st.dataframe(df, height=300)  # Adjust the height as needed for scrollable view
            else:
                st.write("No inventory items found for this warehouse.")

        # Close the database connection
        cursor.close()
        connection.close()

# If running directly, call view_inventory function
if __name__ == "__main__":
    view_inventory()
