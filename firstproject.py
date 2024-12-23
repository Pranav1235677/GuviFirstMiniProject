import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Function to generate a simulated dataset
def generate_data(month):
    categories = [
        "Food", "Transportation", "Bills", "Groceries", "Entertainment", 
        "Healthcare", "Shopping", "Dining", "Travel", "Education",
        "Electricity", "Household Items", "Festive Expenses"
    ]
    
    payment_modes = ["Cash", "Online", "NetBanking", "Credit Card", "Debit Card", "Wallet"]
    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    # Define category-to-description mapping
    category_descriptions = {
        "Food": ["Bought vegetables", "Groceries for home", "Milk and dairy items"],
        "Transportation": ["Car petrol refill", "Train ticket booking", "Bus pass renewal"],
        "Bills": ["Paid electricity bill", "Water bill payment", "Mobile recharge"],
        "Groceries": ["Groceries for home", "Shopping at local market"],
        "Entertainment": ["Dining at a restaurant", "Festival decorations", "New clothes purchase"],
        "Healthcare": ["Doctor consultation fee", "Medicine purchase"],
        "Shopping": ["Shopping at local market", "New clothes purchase"],
        "Dining": ["Dining at a restaurant"],
        "Travel": ["Train ticket booking", "Bus pass renewal"],
        "Education": ["School fees payment", "Purchase of stationery"],
        "Electricity": ["Paid electricity bill"],
        "Household Items": ["House cleaning items", "Repair work at home"],
        "Festive Expenses": ["Festival decorations", "Gift for a family member"]
    }

    data = []
    for _ in range(51):
        random_date = fake.date_between_dates(
            date_start=pd.Timestamp(year=2024, month=month_mapping[month], day=1),
            date_end=pd.Timestamp(year=2024, month=month_mapping[month], day=28)
        )
        category = random.choice(categories)
        data.append({
            "Date": random_date,
            "Category": category,
            "Payment_Mode": random.choice(payment_modes),
            "Description": random.choice(category_descriptions[category]),
            "Amount_Paid": round(random.uniform(10.0, 500.0), 2),
            "Cashback": round(random.uniform(0.0, 20.0), 2),
            "Month": month
        })
    return pd.DataFrame(data)

# Function to initialize the SQLite database with month-specific tables
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    for month in months:
        table_name = month.lower()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                Date TEXT,
                Category TEXT,
                Payment_Mode TEXT,
                Description TEXT,
                Amount_Paid REAL,
                Cashback REAL,
                Month TEXT
            )
        """)
    conn.commit()
    conn.close()

# Function to load data into the appropriate month table
def load_data_to_db(data, month):
    conn = sqlite3.connect('expenses.db')
    table_name = month.lower()
    data.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

# Function to query data from a specific month table
def query_data_from_table(table=None):
    conn = sqlite3.connect('expenses.db')
    if table:
        result = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY Date ASC", conn)
    else:
        # Combine data from all tables
        months = ["january", "february", "march", "april", "may", "june", 
                  "july", "august", "september", "october", "november", "december"]
        result = pd.concat([pd.read_sql_query(f"SELECT * FROM {month}", conn) for month in months], ignore_index=True)
    conn.close()
    return result

# Initialize the database
init_db()

# Apply custom CSS for styling
# Apply custom CSS for styling
def apply_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #dce6f2; /* Set a slightly darker background color */
        }
        h1, h2, h3 {
            color: #6c63ff; /* Keep headers consistent */
        }
        .stButton>button {
            background-color: #28a745; /* Green button */
            color: white; /* Button text color */
            border: none; /* Remove border */
            border-radius: 8px; /* Rounded corners */
            padding: 10px 20px; /* Add padding */
            font-size: 16px; /* Adjust font size */
        }
        .stButton>button:hover {
            background-color: #218838; /* Darker green on hover */
        }
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #36454f; /* Darker background for the sidebar */
            color: white; /* Sidebar text color */
            border-radius: 10px; /* Rounded corners for sidebar */
            padding: 10px; /* Add some padding */
        }
        [data-testid="stSidebar"] .css-1d391kg {
            color: white; /* Change text color in the sidebar */
        }
        [data-testid="stSidebar"] h2 {
            color: #FFD700; /* Change sidebar header color (e.g., to gold) */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Call the custom CSS function
apply_custom_css()

# Main Streamlit app
st.title("Personal Expense Tracker")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose an option",
    ["Generate Data", "View Data", "Visualize Insights", "Run SQL Query", "Run Predefined SQL Queries"]
)

if option == "Generate Data":
    st.subheader("Generate Expense Data")
    month = st.text_input("Enter the month (e.g., January):", "January")
    if st.button("Generate"):
        try:
            data = generate_data(month)
            load_data_to_db(data, month)
            st.success(f"Data for {month} generated and loaded into the database!")
            st.dataframe(data.head())
        except KeyError:
            st.error("Invalid month entered. Please ensure the month is spelled correctly.")

elif option == "View Data":
    st.subheader("View Expense Data")
    scope = st.selectbox("View scope", ["Specific Month", "All Months"])
    if scope == "Specific Month":
        month = st.text_input("Enter the month to view data (e.g., January):", "January")
        if st.button("View"):
            try:
                table = month.lower()
                data = query_data_from_table(table)
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("View All"):
            try:
                data = query_data_from_table()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Visualize Insights":
    st.subheader("Spending Insights")
    scope = st.selectbox("Visualize scope", ["Specific Month", "All Months"])
    if scope == "Specific Month":
        month = st.text_input("Enter the month to visualize data (e.g., January):", "January")
        if st.button("Visualize"):
            try:
                table = month.lower()
                query = f"SELECT Category, SUM(Amount_Paid) as Total_Spent FROM {table} GROUP BY Category"
                conn = sqlite3.connect('expenses.db')
                data = pd.read_sql_query(query, conn)
                conn.close()
                
                # Display Bar Chart
                st.bar_chart(data.set_index("Category"))
                
                # Display Pie Chart
                fig, ax = plt.subplots()
                ax.pie(data['Total_Spent'], labels=data['Category'], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.
                st.pyplot(fig)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("Visualize All"):
            try:
                data = query_data_from_table()
                insights = data.groupby("Category")["Amount_Paid"].sum().reset_index()
                
                # Display Bar Chart
                st.bar_chart(insights.set_index("Category"))
                
                # Display Pie Chart
                fig, ax = plt.subplots()
                ax.pie(insights['Amount_Paid'], labels=insights['Category'], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Run SQL Query":
    st.subheader("Run Custom SQL Query")
    scope = st.selectbox("Query scope", ["Specific Month", "All Months"])
    if scope == "Specific Month":
        month = st.text_input("Enter the month for the query (e.g., January):", "January")
        query = st.text_area("Enter your SQL query:")
        if st.button("Execute"):
            try:
                table = month.lower()
                query = query.replace("{table}", table)
                conn = sqlite3.connect('expenses.db')
                data = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        query = st.text_area("Enter your SQL query for all months:")
        if st.button("Execute All"):
            try:
                data = query_data_from_table()
                conn = sqlite3.connect('expenses.db')
                data.to_sql("expenses_union", conn, if_exists="replace", index=False)
                result = pd.read_sql_query(query.replace("{table}", "expenses_union"), conn)
                conn.close()
                st.dataframe(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")

elif option == "Run Predefined SQL Queries":
    st.subheader("Run Predefined SQL Queries")
    scope = st.selectbox("Query scope", ["Specific Month", "All Months"])
    queries = {
        "Total Spending by Category": "SELECT Category, SUM(Amount_Paid) as Total_Spent FROM {table} GROUP BY Category",
        "Top 5 Highest Spending Transactions": "SELECT * FROM {table} ORDER BY Amount_Paid DESC LIMIT 5",
        "Total Cashback Earned": "SELECT SUM(Cashback) as Total_Cashback FROM {table}",
        "Monthly Spending Breakdown": "SELECT Month, SUM(Amount_Paid) as Total_Spent FROM {table} GROUP BY Month",
        "Average Transaction Amount": "SELECT AVG(Amount_Paid) as Average_Transaction FROM {table}",
        "Total Spending Per Payment Mode": "SELECT Payment_Mode, SUM(Amount_Paid) as Total_Spent FROM {table} GROUP BY Payment_Mode",
        "Minimum Spending in a Transaction": "SELECT MIN(Amount_Paid) as Min_Spent FROM {table}",
        "Maximum Spending in a Transaction": "SELECT MAX(Amount_Paid) as Max_Spent FROM {table}",
        "Number of Transactions Per Category": "SELECT Category, COUNT(*) as Total_Transactions FROM {table} GROUP BY Category",
        "Number of Transactions Per Payment Mode": "SELECT Payment_Mode, COUNT(*) as Total_Transactions FROM {table} GROUP BY Payment_Mode",
        "Top 3 Cashback Earners": "SELECT * FROM {table} ORDER BY Cashback DESC LIMIT 3",
        "Total Spending on Food": "SELECT SUM(Amount_Paid) as Food_Spent FROM {table} WHERE Category = 'Food'",
        "Total Spending on Entertainment": "SELECT SUM(Amount_Paid) as Entertainment_Spent FROM {table} WHERE Category = 'Entertainment'",
        "Transactions Above $200": "SELECT * FROM {table} WHERE Amount_Paid > 200",
        "Transactions Below $50": "SELECT * FROM {table} WHERE Amount_Paid < 50",
        "Distinct Categories": "SELECT DISTINCT Category FROM {table}",
        "Distinct Payment Modes": "SELECT DISTINCT Payment_Mode FROM {table}",
        "Transactions by Weekday": "SELECT strftime('%w', Date) as Weekday, COUNT(*) as Total_Transactions FROM {table} GROUP BY Weekday",
        "Transactions Per Month": "SELECT Month, COUNT(*) as Total_Transactions FROM {table} GROUP BY Month",
        "Cashback Greater than $10": "SELECT * FROM {table} WHERE Cashback > 10",
        "Transactions Without Cashback": "SELECT * FROM {table} WHERE Cashback = 0"
    }
    query_name = st.selectbox("Choose a predefined query", list(queries.keys()))
    if scope == "Specific Month":
        month = st.text_input("Enter the month for the query (e.g., January):", "January")
        if st.button("Run Query"):
            try:
                table = month.lower()
                query = queries[query_name].format(table=table)
                conn = sqlite3.connect('expenses.db')
                data = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(data)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        if st.button("Run Query for All Months"):
            try:
                data = query_data_from_table()
                conn = sqlite3.connect('expenses.db')
                data.to_sql("expenses_union", conn, if_exists="replace", index=False)
                query = queries[query_name].replace("{table}", "expenses_union")
                result = pd.read_sql_query(query, conn)
                conn.close()
                st.dataframe(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")
