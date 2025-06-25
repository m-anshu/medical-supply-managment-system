import streamlit as st
import mysql.connector
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

# Function to add a new warehouse
def add_warehouse():
    st.title("Add Warehouse")

    # Input fields for warehouse details
    warehouse_id = st.number_input("Warehouse ID", min_value=1, step=1)
    warehouse_name = st.text_input("Warehouse Name")
    max_capacity = st.number_input("Maximum Capacity (in boxes)", min_value=1)

    if st.button("Add Warehouse"):
        # Connect to the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor()

            # Check if the warehouse ID already exists
            cursor.execute("SELECT * FROM warehouse WHERE warehouse_id = %s", (warehouse_id,))
            existing_warehouse = cursor.fetchone()

            if existing_warehouse:
                st.error("Warehouse ID already exists. Please choose a different ID.")
            else:
                # Insert new warehouse into the database
                try:
                    cursor.execute("INSERT INTO warehouse (warehouse_id, name, max_capacity) VALUES (%s, %s, %s)",
                                   (warehouse_id, warehouse_name, max_capacity))
                    connection.commit()
                    st.success(f"Warehouse '{warehouse_name}' added with ID {warehouse_id} and capacity of {max_capacity} boxes.")
                except Error as e:
                    st.error(f"Error adding warehouse: {e}")

            # Close the database connection
            cursor.close()
            connection.close()
