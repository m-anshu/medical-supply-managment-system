import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
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

# Function to delete a warehouse and associated medicines
def remove_warehouse():
    st.title("Delete Warehouse")

    # Connect to the database
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Fetch all warehouses to populate the dropdown
        cursor.execute("SELECT warehouse_id, name, max_capacity FROM warehouse")
        warehouses = cursor.fetchall()

        # Create a dropdown for selecting a warehouse to delete
        warehouse_options = {f"{name} (ID: {warehouse_id})": warehouse_id for warehouse_id, name, _ in warehouses}
        selected_warehouse = st.selectbox("Select a Warehouse to Delete", list(warehouse_options.keys()))

        # Get the selected warehouse ID and max capacity
        warehouse_id = warehouse_options[selected_warehouse]
        max_capacity = next((capacity for w_id, _, capacity in warehouses if w_id == warehouse_id), None)

        # Fetch inventory and calculate the current capacity
        cursor.execute("SELECT name, manufacture_date, expiry_date, quantity FROM medicines WHERE warehouse_id = %s", (warehouse_id,))
        inventory_items = cursor.fetchall()

        current_capacity = sum(item[3] for item in inventory_items)  # Sum up the quantities to get the current capacity

        # Display warehouse stats
        st.write(f"### Warehouse Stats for {selected_warehouse}")
        st.write(f"- **Max Capacity:** {max_capacity}")
        st.write(f"- **Current Capacity:** {current_capacity}")

        # Display inventory items
        if inventory_items:
            st.write("#### Inventory Items:")
            df = pd.DataFrame(inventory_items, columns=["Name", "Manufacture Date", "Expiry Date", "Quantity"])
            st.dataframe(df, height=300)
        else:
            st.write("No inventory items found for this warehouse.")

        # Show delete button if user wants to proceed with deletion
        if st.button("Confirm Delete"):
            try:
                # Disable foreign key checks
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

                # Delete associated medicines
                cursor.execute("DELETE FROM medicines WHERE warehouse_id = %s", (warehouse_id,))

                # Delete the warehouse
                cursor.execute("DELETE FROM warehouse WHERE warehouse_id = %s", (warehouse_id,))

                # Re-enable foreign key checks
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

                # Commit the transaction
                connection.commit()
                st.success(f"Warehouse {selected_warehouse} and its associated inventory have been deleted.")

            except Error as e:
                st.error(f"Error deleting warehouse: {e}")
                connection.rollback()

            finally:
                # Re-enable foreign key checks in case of error
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # Close the database connection
        cursor.close()
        connection.close()

# If running directly, call delete_warehouse function
if __name__ == "__main__":
    remove_warehouse()
