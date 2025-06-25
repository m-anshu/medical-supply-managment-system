import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
def low_quantity_medicines_page():
    # Connect to the database
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    # Query to get warehouse names and IDs
    cursor.execute("SELECT warehouse_id, name FROM warehouse")
    warehouses = cursor.fetchall()

    st.title("Low Quantity Medicines by Warehouse")

    # Loop through each warehouse to find medicines with low stock
    for warehouse_id, warehouse_name in warehouses:
        # Query to get medicines in the current warehouse with quantity <= 5
        cursor.execute(
            """
            SELECT name, quantity 
            FROM medicines 
            WHERE warehouse_id = %s AND quantity <= 5
            """, (warehouse_id,)
        )
        low_stock_medicines = cursor.fetchall()

        # Display warehouse information and low-stock medicines
        if low_stock_medicines:
            st.subheader(f"{warehouse_name} (Warehouse ID: {warehouse_id})")
            for medicine_name, quantity in low_stock_medicines:
                st.write(f"- {medicine_name}: {quantity} units")

    # Close the database connection
    cursor.close()
    conn.close()
