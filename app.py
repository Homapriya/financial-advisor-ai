import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt 
from ocr import extract_text
import sqlite3
from chatbot import ask_chatbot
import os


def generate_advice(total, category_totals):
    advice = []

    if total == 0:
        return ["Start adding expenses to get insights."]

    if total > 10000:
        advice.append("Your overall spending is high this month.")

    if "Food" in category_totals:
        percent = category_totals["Food"] / total
        if percent > 0.4:
            advice.append("A large portion of your expenses is on food. Consider reducing outside food.")

    if "Shopping" in category_totals:
        percent = category_totals["Shopping"] / total
        if percent > 0.3:
            advice.append("Shopping expenses are high. Try budgeting your purchases.")

    if "Transport" in category_totals:
        percent = category_totals["Transport"] / total
        if percent > 0.25:
            advice.append("Transport costs are significant. Look for cost-saving options.")

    if total < 5000:
        advice.append("Your spending is under control. Keep it up!")

    return advice

st.title("AI Financial Advisor & Expense Manager")

if "username" not in st.session_state:
    st.session_state["username"] = None

if st.session_state["username"] is None:
    st.warning("Please login first.")
    st.stop()

username = st.session_state["username"]

st.write(f"👤 Logged in as: {username}")

if st.button("🚪 Logout"):

    st.session_state["username"] = None

    st.switch_page("login.py")

#database setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    username TEXT,
    amount INTEGER,
    category TEXT
)
""")

conn.commit()

# Reset Button
if st.button("🔁 Reset All Expenses"):
    st.session_state.expenses = []
    cursor.execute(
        "DELETE FROM expenses WHERE username=?",
        (username,)
    )
    conn.commit()
    st.success("All expenses cleared!")

#Initialize session state
if "expenses" not in st.session_state:

    username = st.session_state.get("username", "Guest")

    cursor.execute(
        "SELECT * FROM expenses WHERE username=?",
        (username,)
    )
    
    rows = cursor.fetchall()

    st.session_state.expenses = [
        {"Amount": r[1], "Category": r[2]}
        for r in rows
    ]
#screenshot upload
st.subheader("Upload Payment Screenshot")

uploaded_file = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file:
    text = extract_text(uploaded_file)

    st.write("Extracted Text:")
    st.write(text)

    amounts = re.findall(r'Rs\s*(\d+)', text)

    if amounts:
        detected_amount = int(amounts[0])
        st.success(f"Detected Amount: Rs {detected_amount}")

        # Auto category detection
        lower_text = text.lower()

        if "swiggy" in lower_text or "zomato" in lower_text:
            detected_category = "Food"
        elif "amazon" in lower_text or "flipkart" in lower_text:
            detected_category = "Shopping"
        elif "uber" in lower_text or "metro" in lower_text:
            detected_category = "Transport"
        else:
            detected_category = "Other"

        st.write(f"Detected Category: {detected_category}")

        if st.button("Add Detected Expense"):
            st.session_state.expenses.append({
                "Amount": detected_amount,
                "Category": detected_category
            })
            
            cursor.execute(
                "INSERT INTO expenses VALUES (?, ?, ?)",
                (username, detected_amount, detected_category)
            )
            
            conn.commit()
            st.success("Expense Added from Screenshot!")

#manual entry 
st.subheader("Enter Expense Details")

amount = st.number_input("Enter amount (Rs)", min_value=0)
category = st.selectbox("Select Category", ["Food", "Shopping", "Transport", "Other"])

if st.button("Add Expense"):
    st.session_state.expenses.append({"Amount": amount, "Category": category})

    cursor.execute(
    "INSERT INTO expenses VALUES (?, ?, ?)",
    (username, amount, category)
    )
    conn.commit()

    st.success("Expense Added Successfully!")
# ======================
# CSV UPLOAD (Week 4)
# ======================

st.subheader("Upload Bank Statement (CSV)")

csv_file = st.file_uploader("Upload CSV file", type=["csv"])

if csv_file:

    csv_data = pd.read_csv(csv_file)

    st.write("Uploaded Data")
    st.dataframe(csv_data)

    if st.button("Add CSV Expenses"):

        for _, row in csv_data.iterrows():

            st.session_state.expenses.append({
                "Amount": row["Amount"],
                "Category": row["Category"]
            })
            
            cursor.execute(
                "INSERT INTO expenses VALUES (?, ?, ?)",
                (username, row["Amount"], row["Category"])
            )
            
        conn.commit()

        st.success("CSV Expenses Added!")

# Show Expenses
if st.session_state.expenses:

    df = pd.DataFrame(st.session_state.expenses)

    st.subheader("📊 Expense Dashboard")
    st.dataframe(df)

    total = df["Amount"].sum()
    st.subheader(f"Total Spending: Rs {total}")

    # Category totals
    category_totals = df.groupby("Category")["Amount"].sum()

    # Bar Chart
    st.subheader("Category-wise Spending")
    st.bar_chart(category_totals)

    # Budget Section
    st.subheader("💰 Monthly Budget")

    budget = st.number_input("Enter your monthly budget (Rs)", min_value=0)

    if budget > 0:
        remaining = budget - total
        st.write("Remaining Budget:", remaining)

        if total > budget:
            st.error("You have exceeded your monthly budget!")

    # Savings Goal Tracker
    st.subheader("🎯 Savings Goal")

    savings_goal = st.number_input("Savings Goal (Rs)", min_value=0)

    if savings_goal > 0:

        saved = max(0, budget - total)

        progress = min(saved / savings_goal, 1.0)

        st.progress(progress)

        st.write(f"Saved Rs {saved} out of Rs {savings_goal}")


    # Expense Prediction

    st.subheader("🔮 Expense Prediction")

    avg_expense = df["Amount"].mean()

    predicted_spending = avg_expense * len(df)

    st.write(f"Estimated future spending: Rs {predicted_spending:.2f}")


    # Spending Insights
    highest_category = category_totals.idxmax()
    highest_amount = category_totals.max()

    st.subheader("📊 Spending Insights")
    st.write("Highest spending category:", highest_category)
    st.write("Amount spent:", highest_amount)

    # Pie Chart
    st.subheader("📈 Spending Distribution")

    fig, ax = plt.subplots()
    ax.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%')
    st.pyplot(fig)

    # AI Advice
    st.subheader("🤖 AI Financial Advice")

    advice_list = generate_advice(total, category_totals)

    for adv in advice_list:
        st.info(adv)
        
        
        

    if total > 10000:
        st.error("Your total spending is high this month. Consider reducing unnecessary expenses.")

    if "Food" in category_totals and category_totals["Food"] > 4000:
        st.warning("You are spending a lot on food. Try cooking more at home.")

    if "Shopping" in category_totals and category_totals["Shopping"] > 5000:
        st.warning("High shopping expenses detected. Consider budgeting better.")

    if total <= 10000 and total > 0:
        st.success("Your spending is under control. Keep it up!")
        
    
    # AI Financial Chatbot
    st.subheader("🤖 AI Financial Chatbot")

    question = st.text_input("Ask any financial question")

    if question:

        prompt = f"""
        You are a personal financial advisor.

        User total spending: {total}
        Highest spending category: {highest_category}

        User question:
        {question}
        """

        answer = ask_chatbot(prompt)

        st.write(answer)