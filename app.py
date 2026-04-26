import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt 
from ocr import extract_text
import sqlite3

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

#database setup
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    amount INTEGER,
    category TEXT
)
""")

conn.commit()

# Reset Button
if st.button("🔁 Reset All Expenses"):
    st.session_state.expenses = []
    cursor.execute("DELETE FROM expenses")
    conn.commit()
    st.success("All expenses cleared!")

#Initialize session state
if "expenses" not in st.session_state:

    cursor.execute("SELECT * FROM expenses")

    rows = cursor.fetchall()

    st.session_state.expenses = [
        {"Amount": r[0], "Category": r[1]}
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
            st.success("Expense Added from Screenshot!")

#manual entry 
st.subheader("Enter Expense Details")

amount = st.number_input("Enter amount (Rs)", min_value=0)
category = st.selectbox("Select Category", ["Food", "Shopping", "Transport", "Other"])

if st.button("Add Expense"):
    st.session_state.expenses.append({"Amount": amount, "Category": category})
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

        st.success("CSV Expenses Added!")

# Show Expenses
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