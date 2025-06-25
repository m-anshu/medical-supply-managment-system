import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
# Database connection function
def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
    )

# Function to fetch all clients
def fetch_clients():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM clients")
    clients = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return clients

# Function to fetch order history for a specific client
def fetch_order_history(username):
    conn = create_connection()
    cursor = conn.cursor()

    # Query to retrieve orders with warehouse names for the selected user
    query = """
        SELECT o.order_id, o.order_date, w.name AS warehouse_name
        FROM orders o
        JOIN warehouse w ON o.warehouse_id = w.warehouse_id
        WHERE o.username = %s
    """
    cursor.execute(query, (username,))
    orders = cursor.fetchall()

    order_history = []
    for order in orders:
        order_id, order_date, warehouse_name = order
        # Query to retrieve items for the current order
        cursor.execute("SELECT medicine_name, quantity FROM order_items WHERE order_id = %s", (order_id,))
        items = cursor.fetchall()
        order_history.append((order_id, warehouse_name, items))

    cursor.close()
    conn.close()
    return order_history

# Client statistics page to display order history of selected client
def client_stats():
    st.title("Client Order History")

    # Step 1: Select a client from dropdown
    clients = fetch_clients()
    selected_client = st.selectbox("Select a Client", clients)

    if selected_client:
        # Step 2: Fetch and display the order history of the selected client
        st.subheader(f"Order History for {selected_client}")

        order_history = fetch_order_history(selected_client)

        if not order_history:
            st.write("No orders found for this client.")
        else:
            for count, (order_id, warehouse_name, items) in enumerate(order_history, start=1):
                st.subheader(f"Order No: {count} ({warehouse_name})")
                if items:
                    for medicine_name, quantity in items:
                        st.write(f"{medicine_name}: {quantity}")
                else:
                    st.write("No items found for this order.")

# If running directly, call client_stats function
if __name__ == "__main__":
    client_stats()
