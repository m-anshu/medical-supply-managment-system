import streamlit as st
import mysql.connector
import pandas as pd
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

# Function to add a batch of medicines under a single supply ID
def add_medicine_batch(medicines, warehouse_id):
    conn = create_connection()
    cursor = conn.cursor()
    supplier_username = st.session_state['username']  # Get the logged-in supplier's username
    supply_date = datetime.now()

    try:
        # Ensure the supplier exists; if not, add them to the supplier table
        cursor.execute("SELECT * FROM supplier WHERE username = %s", (supplier_username,))
        supplier_exists = cursor.fetchone()

        if not supplier_exists:
            cursor.execute("INSERT INTO supplier (username) VALUES (%s)", (supplier_username,))
            conn.commit()
            st.success(f"Supplier '{supplier_username}' added successfully.")

        # Create a new supply entry including warehouse_id
        cursor.execute(
            "INSERT INTO supply (username, supply_date, warehouse_id) VALUES (%s, %s, %s)",
            (supplier_username, supply_date, warehouse_id)  # Include warehouse_id
        )
        supply_id = cursor.lastrowid  # Capture the generated supply_id

        # Process each medicine
        for name, manufacture_date, expiry_date, quantity in medicines:
            # Check if the medicine already exists
            cursor.execute("SELECT quantity FROM medicines WHERE name = %s AND warehouse_id = %s", (name, warehouse_id))
            result = cursor.fetchone()

            if result:
                # Update existing medicine quantity
                new_quantity = result[0] + quantity
                cursor.execute(
                    "UPDATE medicines SET quantity = %s, manufacture_date = %s, expiry_date = %s WHERE name = %s AND warehouse_id = %s",
                    (new_quantity, manufacture_date, expiry_date, name, warehouse_id)
                )
                st.info(f"Updated quantity of '{name}' to {new_quantity}.")
            else:
                # Insert new medicine record
                cursor.execute(
                    "INSERT INTO medicines (name, manufacture_date, expiry_date, quantity, warehouse_id) VALUES (%s, %s, %s, %s, %s)",
                    (name, manufacture_date, expiry_date, quantity, warehouse_id)
                )
                st.info(f"Medicine '{name}' added successfully.")

            # Insert into supply_items with the generated supply_id
            cursor.execute(
                "INSERT INTO supply_items (supply_id, medicine_name, quantity) VALUES (%s, %s, %s)",
                (supply_id, name, quantity)
            )

        conn.commit()
        st.success(f"Supply batch with ID {supply_id} logged successfully.")

    except mysql.connector.Error as err:
        st.error(f"Error adding/updating medicines: {err}")
    finally:
        cursor.close()
        conn.close()

# Function to fetch and display all medicines
def fetch_all_medicines(warehouse_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, manufacture_date, expiry_date, quantity FROM medicines WHERE warehouse_id = %s", (warehouse_id,))
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return medicines

# Function to fetch all warehouses for selection
def fetch_warehouses():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT warehouse_id, name, max_capacity FROM warehouse")
    warehouses = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return warehouses

# Function to get the current total quantity of medicines in the selected warehouse
def get_current_quantity(warehouse_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(quantity) FROM medicines WHERE warehouse_id = %s", (warehouse_id,))
    current_quantity = cursor.fetchone()[0] or 0  # Default to 0 if no medicines are found
    cursor.close()
    conn.close()
    
    return current_quantity

# Add multiple medicines page
def add_medicine_page():
    st.title("Add Multiple Medicines")

    # Check if user is logged in and has the appropriate role
    if st.session_state.get('logged_in') and st.session_state.get('role') in ["Supplier", "Employee"]:
        # Fetch warehouses
        warehouses = fetch_warehouses()
        warehouse_options = {f"{name} (ID: {warehouse_id}, Max Capacity: {max_capacity})": (warehouse_id, max_capacity) for warehouse_id, name, max_capacity in warehouses}
        selected_warehouse = st.selectbox("Select a Warehouse", list(warehouse_options.keys()))

        warehouse_id, max_capacity = warehouse_options[selected_warehouse]

        # Display current medicines in the selected warehouse
        st.subheader("Current Medicines in Database")
        medicines = fetch_all_medicines(warehouse_id)

        if medicines:
            df = pd.DataFrame(medicines, columns=["Name", "Manufacture Date", "Expiry Date", "Quantity"])
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No medicines found in the database.")
        
        # Step 1: Select the number of medicines to add
        st.subheader("Add New Medicines")
        num_medicines = st.number_input("Number of different medicines to add", min_value=1, step=1)
        proceed_button = st.button("Proceed to Enter Medicine Details")

        # Step 2: Show input fields based on the number of medicines selected
        if proceed_button:
            st.session_state['num_medicines'] = num_medicines

        if 'num_medicines' in st.session_state:
            medicine_data = []
            with st.form("add_medicines_form"):
                for i in range(st.session_state['num_medicines']):
                    st.write(f"### Medicine {i + 1}")
                    name = st.text_input(f"Medicine Name {i + 1}", key=f"name_{i}")
                    manufacture_date = st.date_input(f"Manufacture Date {i + 1}", key=f"manufacture_date_{i}")
                    expiry_date = st.date_input(f"Expiry Date {i + 1}", key=f"expiry_date_{i}")
                    quantity = st.number_input(f"Quantity for Medicine {i + 1}", min_value=1, step=1, key=f"quantity_{i}")

                    # Append medicine details if the name is provided
                    if name:
                        medicine_data.append((name, manufacture_date, expiry_date, quantity))

                submit_button = st.form_submit_button("Add Medicines")
                if submit_button:
                    if not medicine_data:
                        st.warning("Please enter at least one medicine with a name.")
                    else:
                        current_quantity = get_current_quantity(warehouse_id)
                        total_new_quantity = sum(q for _, _, _, q in medicine_data) + current_quantity

                        if total_new_quantity > max_capacity:
                            st.warning(f"Cannot add medicines. Total quantity would exceed maximum capacity of {max_capacity}.")
                        else:
                            add_medicine_batch(medicine_data, warehouse_id)
    else:
        st.error("You do not have permission to access this page.")

# Call the add_medicine_page function
if __name__ == "__main__":
    add_medicine_page()
