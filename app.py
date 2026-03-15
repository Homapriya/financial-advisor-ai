import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt 
from ocr import extract_text

st.title("AI Financial Advisor & Expense Manager")

#Initialize session state
if "expenses" not in st.session_state:
    st.session_state.expenses = []
    
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

# Show Expenses
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    st.subheader("All Expenses")
    st.dataframe(df)

    total = df["Amount"].sum()
    st.subheader(f"Total Spending: Rs {total}")
    
    category_totals = df.groupby("Category")["Amount"].sum()
    st.subheader("Category-wise Spending")
    st.bar_chart(category_totals)
    
        # Budget Section
    st.subheader("Monthly Budget")

    budget = st.number_input("Enter your monthly budget (Rs)", min_value=0)

    if budget > 0:
        remaining = budget - total
        st.write("Remaining Budget:", remaining)

        if total > budget:
            st.error("You have exceeded your monthly budget!")

    # Category totals
    category_totals = df.groupby("Category")["Amount"].sum()

    # Bar Chart
    st.subheader("Category-wise Spending")
    st.bar_chart(category_totals)

    # Spending Insights
    highest_category = category_totals.idxmax()
    highest_amount = category_totals.max()

    st.subheader("Spending Insights")
    st.write("Highest spending category:", highest_category)
    st.write("Amount spent:", highest_amount)

    # Pie Chart
    st.subheader("Spending Distribution")

    fig, ax = plt.subplots()
    ax.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%')
    st.pyplot(fig)

    

    # Financial Advice Section
    st.subheader("Financial Advice")

    if total > 10000:
        st.error("Your total spending is high this month. Consider reducing unnecessary expenses.")

    if "Food" in category_totals and category_totals["Food"] > 4000:
        st.warning("You are spending a lot on food. Try cooking more at home.")

    if "Shopping" in category_totals and category_totals["Shopping"] > 5000:
        st.warning("High shopping expenses detected. Consider budgeting better.")

    if total <= 10000 and total > 0:
        st.success("Your spending is under control. Keep it up!")