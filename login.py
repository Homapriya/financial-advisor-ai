import streamlit as st
import sqlite3

# Database connection
conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
conn.commit()

st.title("🔐 Login System")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# Register
if choice == "Register":

    st.subheader("Create New Account")

    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")

    if st.button("Register"):

        try:
            cursor.execute(
                "INSERT INTO users VALUES (?, ?)",
                (new_user, new_password)
            )
            
            conn.commit()
            st.success("Registration Successful!")
            
        except sqlite3.IntegrityError:
            st.error("Username already exists. Please choose another username.")
        
        st.info("Go to Login Menu")

# Login
elif choice == "Login":

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        result = cursor.fetchone()

        if result:
            with open("current_user.txt", "w") as f:
                f.write(username)
                
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid Username or Password")