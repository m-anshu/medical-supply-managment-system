import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
# Function to display order history based on the logged-in username
def order_history_page(username):
    st.title("Order History")

    # Establish connection to the MySQL database
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        cursor = conn.cursor()

        # Query to retrieve orders with warehouse names for the logged-in user
        query = """
            SELECT o.order_id, o.order_date, w.name AS warehouse_name
            FROM orders o
            JOIN warehouse w ON o.warehouse_id = w.warehouse_id
            WHERE o.username = %s
        """
        cursor.execute(query, (username,))
        orders = cursor.fetchall()

        if not orders:
            st.write("No orders found.")
            return

        # Loop through each order and retrieve associated items
        for count, order in enumerate(orders, start=1):
            order_id, order_date, warehouse_name = order
            st.subheader(f"Order No: {count} ({warehouse_name})")

            # Query to retrieve items for the current order
            cursor.execute("SELECT medicine_name, quantity FROM order_items WHERE order_id = %s", (order_id,))
            items = cursor.fetchall()

            # Display items for the current order
            if items:
                for item in items:
                    medicine_name, quantity = item
                    st.write(f"{medicine_name}: {quantity}")
            else:
                st.write("No items found for this order.")

    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    
    finally:
        if conn:
            cursor.close()
            conn.close()
