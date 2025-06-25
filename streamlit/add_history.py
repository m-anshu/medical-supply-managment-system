import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
# Function to display supply history based on the logged-in username
def supply_history_page(username):
    st.title("Supply History")

    # Establish connection to the MySQL database
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        # Query to retrieve supplies for the logged-in user along with warehouse information
        cursor.execute("""
            SELECT s.supply_id, s.username, s.supply_date, w.name 
            FROM supply s
            JOIN warehouse w ON s.warehouse_id = w.warehouse_id
            WHERE s.username = %s
        """, (username,))
        
        supplies = cursor.fetchall()

        if not supplies:
            st.write("No supply records found.")
            return

        # Loop through each supply and retrieve associated items
        for supply in supplies:
            supply_id, username, supply_date, warehouse_name = supply
            st.subheader(f"Supply ID: {supply_id} (Warehouse: {warehouse_name})")
            st.write(f"Supply Date: {supply_date}")

            # Query to retrieve items for the current supply
            cursor.execute("SELECT medicine_name, quantity FROM supply_items WHERE supply_id = %s", (supply_id,))
            items = cursor.fetchall()

            # Display items for the current supply
            if items:
                for item in items:
                    medicine_name, quantity = item
                    st.write(f"- {medicine_name} (Quantity: {quantity})")
            else:
                st.write("No items found for this supply.")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    
    finally:
        if conn:
            cursor.close()
            conn.close()
