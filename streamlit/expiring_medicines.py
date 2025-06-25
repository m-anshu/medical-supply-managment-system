import streamlit as st
import mysql.connector
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
def expiring_medicines_page():
    # Connect to the database
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()

    # Calculate the date two months from today
    today = datetime.today()
    two_months_from_today = today + timedelta(days=60)

    # Query to get warehouse names and IDs
    cursor.execute("SELECT warehouse_id, name FROM warehouse")
    warehouses = cursor.fetchall()

    st.title("Expiring Medicines by Warehouse")

    # Loop through each warehouse to find medicines expiring within two months
    for warehouse_id, warehouse_name in warehouses:
        # Query to get medicines in the current warehouse with expiry date within two months
        cursor.execute(
            """
            SELECT name, expiry_date 
            FROM medicines 
            WHERE warehouse_id = %s AND expiry_date <= %s
            """, (warehouse_id, two_months_from_today)
        )
        expiring_medicines = cursor.fetchall()

        # Display warehouse information and expiring medicines
        if expiring_medicines:
            st.subheader(f"{warehouse_name} (Warehouse ID: {warehouse_id})")
            for medicine_name, expiry_date in expiring_medicines:
                st.write(f"- {medicine_name}: Expires on {expiry_date}")

    # Close the database connection
    cursor.close()
    conn.close()
