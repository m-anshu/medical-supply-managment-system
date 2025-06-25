import streamlit as st
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv
def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def register_user_page():
    st.subheader("Register a New User")

    # Input fields for user registration
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Client", "Supplier", "Employee"])  # Updated to include all roles

    if st.button("Register"):
        register_user(username, password, role)

def register_user(username, password, role):
    if username_exists(username):
        st.error("Username already exists! Please choose a different username.")
        return

    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        # Insert the new user into the 'users' table
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", 
                       (username, hashed_password, role))
        conn.commit()
        st.success("User registered successfully!")
    except Exception as e:
        st.error(f"Error during registration: {e}")
    finally:
        cursor.close()
        conn.close()

def username_exists(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None
