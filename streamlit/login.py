# login.py

import streamlit as st
import mysql.connector  # MySQL connector for Python
import bcrypt
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

# Hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify a password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Check if username already exists
def username_exists(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    return exists

# Register a new user
def register_user(username, password, role):
    if username_exists(username):
        st.error("Username already exists! Please choose a different username.")
        return

    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", 
                       (username, hashed_password, role))
        conn.commit()
        st.success("User registered successfully!")
    except Exception as e:
        st.error(f"Error during registration: {e}")
    finally:
        cursor.close()
        conn.close()

# Authenticate user
def authenticate_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and check_password(password, result[0]):
        return result[1]  # Returns role if authenticated
    return None

# Define the login and register UI in a function
def login_page():
    st.title("Login/Register")

    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            role = authenticate_user(username, password)
            if role:
                st.success(f"Logged in as {role}")
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username  # Store the username in session state
                print("TESTCASE UT-01 PASSED")
            else:
                print("TESTCASE UT-02 PASSED")
                st.error("Incorrect username or password")

    elif choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Client"])
        if st.button("Register"):
            register_user(username, password, role)
