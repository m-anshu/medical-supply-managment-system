import streamlit as st
import mysql.connector
from datetime import datetime
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

# Function to fetch all warehouses
def fetch_warehouses():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT warehouse_id, name FROM warehouse")
    warehouses = cursor.fetchall()
    cursor.close()
    conn.close()
    return warehouses

# Function to fetch medicines based on warehouse ID and search query
def fetch_medicines_by_warehouse(warehouse_id, search_query=""):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM medicines WHERE warehouse_id = %s"
    params = (warehouse_id,)
    if search_query:
        query += " AND name LIKE %s"
        params += ('%' + search_query + '%',)
    cursor.execute(query, params)
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return medicines

# Function to add a new client if they don't exist
def add_client_if_not_exists(username):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clients WHERE username = %s", (username,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO clients (username) VALUES (%s)", (username,))
            conn.commit()
    except mysql.connector.Error as err:
        st.error(f"Error adding client: {str(err)}")
    finally:
        cursor.close()
        conn.close()

# Function to place an order with multiple items
def place_order(username, items, warehouse_id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Create a new order entry in the orders table
        order_date = datetime.now()
        cursor.execute("INSERT INTO orders (username, order_date, warehouse_id) VALUES (%s, %s, %s)", (username, order_date, warehouse_id))
        order_id = cursor.lastrowid  # Get the generated order ID

        for medicine_name, order_quantity in items:
            # Check the available stock for the medicine
            cursor.execute("SELECT quantity FROM medicines WHERE name = %s AND warehouse_id = %s", (medicine_name, warehouse_id))
            available_quantity = cursor.fetchone()

            if available_quantity is None or available_quantity[0] < order_quantity:
                st.error(f"Cannot place order. Only {available_quantity[0] if available_quantity else 0} of {medicine_name} is available.")
                continue
            
            # Insert each item into the order_items table with the same order ID
            cursor.execute(
                "INSERT INTO order_items (order_id, medicine_name, quantity) VALUES (%s, %s, %s)",
                (order_id, medicine_name, order_quantity)
            )
            
            # Update the quantity in the medicines table
            cursor.execute(
                "UPDATE medicines SET quantity = quantity - %s WHERE name = %s AND warehouse_id = %s",
                (order_quantity, medicine_name, warehouse_id)
            )

        conn.commit()
        st.success(f"Order placed successfully with Order ID: {order_id}")
    except mysql.connector.Error as err:
        st.error("Error placing order: " + str(err))
    finally:
        cursor.close()
        conn.close()

# Client Order Page
def order_page():
    st.title("Order Medicines")

    # Get the username from the session state
    username = st.session_state.get('username', None)
    if username:
        add_client_if_not_exists(username)  # Ensure client exists in the database

        # Step 1: Select a warehouse
        warehouses = fetch_warehouses()
        warehouse_options = {name: warehouse_id for warehouse_id, name in warehouses}
        selected_warehouse = st.selectbox("Select a Warehouse", list(warehouse_options.keys()))

        # Step 2: Fetch medicines for the selected warehouse
        warehouse_id = warehouse_options[selected_warehouse]
        
        # Search bar for medicines within the selected warehouse
        search_query = st.text_input("Search for medicines in selected warehouse")
        medicines = fetch_medicines_by_warehouse(warehouse_id, search_query)

        # Show available medicines in a scrollable table
        if medicines:
            st.write("Available Medicines in Selected Warehouse:")

            medicines_data = [{"Name": med[1], "Expiry Date": med[3], "Quantity": med[4]} for med in medicines]
            st.dataframe(medicines_data, height=200)  # Making the table scrollable with limited height

            selected_medicines = []
            for medicine in medicines:
                name, quantity = medicine[1], medicine[4]  # Adjust indexing as per fetch structure
                st.write(f"**{name}**: {quantity} in stock")
                
                order_quantity = st.number_input(f"Quantity for {name}:", min_value=0, max_value=quantity, step=1)
                
                if order_quantity > 0:
                    selected_medicines.append((name, order_quantity))

            if st.button("Place Order"):
                if selected_medicines:
                    place_order(username, selected_medicines, warehouse_id)
                else:
                    st.warning("No medicines selected for the order.")
        else:
            st.write("No medicines found in the selected warehouse.")
    else:
        st.error("Client is not logged in.")

# Call the order_page function
if __name__ == "__main__":
    order_page()
