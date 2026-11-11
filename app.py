import os
import streamlit as st
import pandas as pd
import numpy as np
import mysql.connector
from io import StringIO
from datetime import datetime

# ---------------------------------------------------
# Streamlit page setup
# ---------------------------------------------------
st.set_page_config(
    page_title="Food Wastage Management – EDA, Queries & Prediction",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# Database helpers
# ---------------------------------------------------
def get_db_setting(name, default=None):
    env_value = os.getenv(f"MYSQL_{name.upper()}")
    if env_value is not None:
        return env_value
    try:
        return st.secrets.get("mysql", {}).get(name, default)
    except Exception:
        return default

def get_connection():
    config = {
        "host": get_db_setting("host", "localhost"),
        "user": get_db_setting("user", "root"),
        "password": get_db_setting("password", ""),
        "database": get_db_setting("database", "food_wastage_db2"),
    }
    return mysql.connector.connect(**config)

@st.cache_data(ttl=120)
def run_query(query: str, params: tuple | None = None) -> pd.DataFrame:
    conn = get_connection()
    try:
        if params is None:
            df = pd.read_sql(query, conn)
        else:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            cursor.close()
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def execute_cud_query(query: str, params: tuple | None = None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def download_df_button(df: pd.DataFrame, label: str, file_prefix: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ---------------------------------------------------
# Sidebar filters
# ---------------------------------------------------
st.sidebar.header("🔎 Global Filters")

try:
    cities_df = run_query("SELECT DISTINCT City FROM Providers UNION SELECT DISTINCT City FROM Receivers;")
    city_options = sorted([c for c in cities_df["City"].dropna().astype(str).tolist() if c and c != "N/A"])
except Exception:
    city_options = []

try:
    ptype_df = run_query("SELECT DISTINCT Provider_Type FROM Providers;")
    provider_type_options = sorted([x for x in ptype_df["Provider_Type"].dropna().astype(str).tolist() if x and x != "N/A"])
except Exception:
    provider_type_options = []

try:
    meal_df = run_query("SELECT DISTINCT Meal_Type FROM Food_Listings;")
    meal_options = sorted([x for x in meal_df["Meal_Type"].dropna().astype(str).tolist() if x and x != "N/A"])
except Exception:
    meal_options = []

selected_city = st.sidebar.selectbox("City (optional)", options=["All"] + city_options, index=0)
selected_ptype = st.sidebar.selectbox("Provider Type (optional)", options=["All"] + provider_type_options, index=0)
selected_meal = st.sidebar.selectbox("Meal Type (optional)", options=["All"] + meal_options, index=0)

def where_snippets():
    wheres = []
    params = []

    if selected_city != "All":
        wheres.append("(p.City = %s OR r.City = %s OR fl.Location = %s)")
        params.extend([selected_city, selected_city, selected_city])

    if selected_ptype != "All":
        wheres.append("(p.Provider_Type = %s OR fl.Provider_Type = %s)")
        params.extend([selected_ptype, selected_ptype])

    if selected_meal != "All":
        wheres.append("fl.Meal_Type = %s")
        params.append(selected_meal)

    if wheres:
        return "WHERE " + " AND ".join(wheres), tuple(params)
    return "", tuple()

# ---------------------------------------------------
# Tabs
# ---------------------------------------------------
home_tab, eda_tab, queries_tab, prediction_tab, crud_tab, learner_queries_tab, about_tab = st.tabs(
    ["🏠 Home", "📊 EDA", "🧮 Queries (15)", "🤖 Prediction", "📝 CRUD Operations", "🧑‍💻 Learner SQL Queries", "ℹ️ About"]
)

# ---------------------------------------------------
# HOME
# ---------------------------------------------------
with home_tab:
    st.title("🍽 Local Food Wastage Management – Dashboard")
    st.markdown("""
**Includes:** EDA, 15 business queries, CSV export, and a simple prediction demo.

**Schema**
- **Providers(Provider_ID, Name, Provider_Type, Address, City, Contact)**
- **Receivers(Receiver_ID, Name, Receiver_Type, City, Contact)**
- **Food_Listings(Food_ID, Provider_ID, Food_Name, Food_Type, Meal_Type, Quantity, Expiry_Date, Location, Provider_Type)**
- **Claims(Claim_ID, Food_ID, Receiver_ID, Timestamp, Status)**
""")

    c1, c2, c3, c4 = st.columns(4)
    try:
        total_providers = run_query("SELECT COUNT(*) AS c FROM Providers;")["c"].iloc[0]
        total_receivers = run_query("SELECT COUNT(*) AS c FROM Receivers;")["c"].iloc[0]
        total_listings = run_query("SELECT COUNT(*) AS c FROM Food_Listings;")["c"].iloc[0]
        total_claims = run_query("SELECT COUNT(*) AS c FROM Claims;")["c"].iloc[0]
    except Exception:
        total_providers = total_receivers = total_listings = total_claims = 0

    c1.metric("Total Providers", f"{total_providers}")
    c2.metric("Total Receivers", f"{total_receivers}")
    c3.metric("Total Listings", f"{total_listings}")
    c4.metric("Total Claims", f"{total_claims}")

    st.info("Use the filters in the sidebar to tailor EDA and some queries.")

# ---------------------------------------------------
# EDA
# ---------------------------------------------------
with eda_tab:
    st.header("📊 Exploratory Data Analysis")

    st.subheader("Providers by City")
    q = "SELECT City, COUNT(*) AS Providers FROM Providers GROUP BY City ORDER BY Providers DESC;"
    df = run_query(q)
    if not df.empty:
        st.bar_chart(df.set_index("City"))
        download_df_button(df, "Download CSV – Providers by City", "providers_by_city")
    else:
        st.warning("No provider data found.")

    st.subheader("Food Type Distribution")
    q = "SELECT Food_Type, COUNT(*) AS CountType FROM Food_Listings GROUP BY Food_Type ORDER BY CountType DESC;"
    df = run_query(q)
    if not df.empty:
        st.bar_chart(df.set_index("Food_Type"))
        download_df_button(df, "Download CSV – Food Type Distribution", "food_type_distribution")
    else:
        st.warning("No food listings found.")

    st.subheader("Meal Type Distribution")
    q = "SELECT Meal_Type, COUNT(*) AS CountMeal FROM Food_Listings GROUP BY Meal_Type ORDER BY CountMeal DESC;"
    df = run_query(q)
    if not df.empty:
        st.bar_chart(df.set_index("Meal_Type"))
        download_df_button(df, "Download CSV – Meal Type Distribution", "meal_type_distribution")
    else:
        st.warning("No meal type data found.")

    st.subheader("Claim Status Breakdown (%)")
    q = """
        SELECT Status,
                ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims)), 2) AS Percentage
        FROM Claims
        GROUP BY Status;
    """
    df = run_query(q)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        download_df_button(df, "Download CSV – Claim Status %", "claim_status_percentage")
    else:
        st.warning("No claims found.")

# ---------------------------------------------------
# QUERIES (All 18)
# ---------------------------------------------------
with queries_tab:
    st.header("🧮 Business Queries (All 18)")
    st.caption("Results update with sidebar filters where applicable.")

    wh_snip, params = where_snippets()

    st.subheader("📌 Providers & Receivers")

    # 1. Count of food providers per city
    q1 = f"SELECT City, COUNT(*) AS Total_Providers FROM Providers {wh_snip} GROUP BY City;"
    df1 = run_query(q1, params)
    st.markdown("**1. Providers per City**")
    st.dataframe(df1, use_container_width=True)
    download_df_button(df1, "Download CSV – Q1", "q01_providers_city")

    # 2. Count of receivers per city
    q2 = f"SELECT City, COUNT(*) AS Total_Receivers FROM Receivers {wh_snip} GROUP BY City;"
    df2 = run_query(q2, params)
    st.markdown("**2. Receivers per City**")
    st.dataframe(df2, use_container_width=True)
    download_df_button(df2, "Download CSV – Q2", "q02_receivers_city")

    # 3. Provider type contributing most food
    q3 = f"""
    SELECT Provider_Type, COUNT(*) AS Total_Food_Listings
    FROM Food_Listings
    {wh_snip}
    GROUP BY Provider_Type
    ORDER BY Total_Food_Listings DESC
    LIMIT 1;
    """
    df3 = run_query(q3, params)
    st.markdown("**3. Top Provider Type by Food Listings**")
    st.dataframe(df3, use_container_width=True)
    download_df_button(df3, "Download CSV – Q3", "q03_top_provider_type")

    # 4. Contact info of providers in a specific city
    city_for_q4 = selected_city if selected_city != "All" else "Bangalore"
    q4 = "SELECT Name, Contact FROM Providers WHERE City=%s;"
    df4 = run_query(q4, (city_for_q4,))
    st.markdown(f"**4. Provider Contacts in {city_for_q4}**")
    st.dataframe(df4, use_container_width=True)
    download_df_button(df4, "Download CSV – Q4", "q04_provider_contacts")

    # 5. Top receivers by number of claims
    q5 = """
    SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
    FROM Receivers r
    JOIN Claims c ON r.Receiver_ID=c.Receiver_ID
    GROUP BY r.Name
    ORDER BY Total_Claims DESC
    LIMIT 5;
    """
    df5 = run_query(q5)
    st.markdown("**5. Top Receivers by Number of Claims**")
    st.dataframe(df5, use_container_width=True)
    download_df_button(df5, "Download CSV – Q5", "q05_top_receivers")

    st.subheader("📌 Food Listings & Availability")

    # 6. Total quantity of food available
    q6 = "SELECT SUM(Quantity) AS Total_Food_Quantity FROM Food_Listings;"
    df6 = run_query(q6)
    st.markdown("**6. Total Food Quantity Available**")
    st.dataframe(df6, use_container_width=True)
    download_df_button(df6, "Download CSV – Q6", "q06_total_food_qty")

    # 7. City with highest number of food listings
    q7 = "SELECT Location AS City, COUNT(*) AS Total_Listings FROM Food_Listings GROUP BY Location ORDER BY Total_Listings DESC LIMIT 1;"
    df7 = run_query(q7)
    st.markdown("**7. City with Most Food Listings**")
    st.dataframe(df7, use_container_width=True)
    download_df_button(df7, "Download CSV – Q7", "q07_top_city_listings")

    # 8. Most commonly available food types
    q8 = "SELECT Food_Type, COUNT(*) AS Count FROM Food_Listings GROUP BY Food_Type ORDER BY Count DESC LIMIT 5;"
    df8 = run_query(q8)
    st.markdown("**8. Most Commonly Available Food Types**")
    st.dataframe(df8, use_container_width=True)
    download_df_button(df8, "Download CSV – Q8", "q08_common_food_types")

    # 9. Total quantity of each food type
    q9 = "SELECT Food_Type, SUM(Quantity) AS Total_Quantity FROM Food_Listings GROUP BY Food_Type;"
    df9 = run_query(q9)
    st.markdown("**9. Total Quantity per Food Type**")
    st.dataframe(df9, use_container_width=True)
    download_df_button(df9, "Download CSV – Q9", "q09_total_qty_per_food_type")

    # 10. Total quantity per provider
    q10 = "SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Quantity FROM Food_Listings f JOIN Providers p ON f.Provider_ID=p.Provider_ID GROUP BY p.Name;"
    df10 = run_query(q10)
    st.markdown("**10. Total Quantity per Provider**")
    st.dataframe(df10, use_container_width=True)
    download_df_button(df10, "Download CSV – Q10", "q10_total_qty_per_provider")

    st.subheader("📌 Claims & Distribution")

    # 11. Claims per food item
    q11 = "SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims FROM Food_Listings f LEFT JOIN Claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_Name ORDER BY Total_Claims DESC;"
    df11 = run_query(q11)
    st.markdown("**11. Number of Claims per Food Item**")
    st.dataframe(df11, use_container_width=True)
    download_df_button(df11, "Download CSV – Q11", "q11_claims_per_food_item")

    # 12. Provider with highest successful claims
    q12 = "SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Completed_Claims FROM Claims c JOIN Food_Listings f ON c.Food_ID=f.Food_ID JOIN Providers p ON f.Provider_ID=p.Provider_ID WHERE c.Status='Completed' GROUP BY p.Name ORDER BY Completed_Claims DESC LIMIT 1;"
    df12 = run_query(q12)
    st.markdown("**12. Provider with Highest Successful Claims**")
    st.dataframe(df12, use_container_width=True)
    download_df_button(df12, "Download CSV – Q12", "q12_top_provider_completed_claims")

    # 13. Percentage of claims by status
    q13 = "SELECT Status, ROUND(COUNT(*)*100/(SELECT COUNT(*) FROM Claims),2) AS Percentage FROM Claims GROUP BY Status;"
    df13 = run_query(q13)
    st.markdown("**13. Claims Status Percentage**")
    st.dataframe(df13, use_container_width=True)
    download_df_button(df13, "Download CSV – Q13", "q13_claim_status_percent")

    st.subheader("📌 Analysis & Insights")

    # 14. Average quantity claimed per receiver
    q14 = "SELECT r.Name AS Receiver_Name, ROUND(AVG(f.Quantity),2) AS Avg_Quantity_Claimed FROM Claims c JOIN Receivers r ON c.Receiver_ID=r.Receiver_ID JOIN Food_Listings f ON c.Food_ID=f.Food_ID GROUP BY r.Name ORDER BY Avg_Quantity_Claimed DESC;"
    df14 = run_query(q14)
    st.markdown("**14. Average Quantity Claimed per Receiver**")
    st.dataframe(df14, use_container_width=True)
    download_df_button(df14, "Download CSV – Q14", "q14_avg_qty_receiver")

    # 15. Most claimed meal type
    q15 = "SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims FROM Claims c JOIN Food_Listings f ON c.Food_ID=f.Food_ID GROUP BY f.Meal_Type ORDER BY Total_Claims DESC;"
    df15 = run_query(q15)
    st.markdown("**15. Most Claimed Meal Type**")
    st.dataframe(df15, use_container_width=True)
    download_df_button(df15, "Download CSV – Q15", "q15_most_claimed_meal")

    # 16. Total quantity donated per provider
    q16 = "SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Donated FROM Food_Listings f JOIN Providers p ON f.Provider_ID=p.Provider_ID GROUP BY p.Name ORDER BY Total_Donated DESC;"
    df16 = run_query(q16)
    st.markdown("**16. Total Quantity Donated per Provider**")
    st.dataframe(df16, use_container_width=True)
    download_df_button(df16, "Download CSV – Q16", "q16_total_donated_per_provider")

    # 17. Top 5 receivers by total claimed quantity
    q17 = "SELECT r.Name AS Receiver_Name, SUM(f.Quantity) AS Total_Claimed FROM Claims c JOIN Receivers r ON c.Receiver_ID=r.Receiver_ID JOIN Food_Listings f ON c.Food_ID=f.Food_ID GROUP BY r.Name ORDER BY Total_Claimed DESC LIMIT 5;"
    df17 = run_query(q17)
    st.markdown("**17. Top 5 Receivers by Total Claimed Quantity**")
    st.dataframe(df17, use_container_width=True)
    download_df_button(df17, "Download CSV – Q17", "q17_top5_receivers_claimed_qty")

    # 18. Least claimed food types
    q18 = "SELECT f.Food_Type, COUNT(c.Claim_ID) AS Claims_Count FROM Food_Listings f LEFT JOIN Claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_Type ORDER BY Claims_Count ASC;"
    df18 = run_query(q18)
    st.markdown("**18. Least Claimed Food Types**")
    st.dataframe(df18, use_container_width=True)
    download_df_button(df18, "Download CSV – Q18", "q18_least_claimed_food_types")

# ---------------------------------------------------
# PREDICTION
# ---------------------------------------------------
with prediction_tab:
    st.header("🤖 Prediction – Which city will likely have the most available food next month?")
    st.caption("Lightweight linear trend on monthly total quantity per city (based on Food_Listings.Expiry_Date).")

    q = "SELECT Location AS City, Expiry_Date, Quantity FROM Food_Listings WHERE Expiry_Date IS NOT NULL"
    df = run_query(q)
    if df.empty:
        st.warning("No dated food listing data available for prediction.")
    else:
        df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce")
        df = df.dropna(subset=["Expiry_Date"])
        df["ym"] = df["Expiry_Date"].dt.to_period("M").astype(str)

        monthly = df.groupby(["City", "ym"])["Quantity"].sum().reset_index().sort_values(["City", "ym"])
        preds = []
        for city, g in monthly.groupby("City"):
            g = g.copy()
            t = pd.to_datetime(g["ym"] + "-01")
            x = (t - t.min()).dt.days.values.astype(float)
            y = g["Quantity"].values.astype(float)
            if len(x) >= 2 and y.sum() > 0:
                coeffs = np.polyfit(x, y, 1)
                next_x = x.max() + 30
                y_pred = float(np.polyval(coeffs, next_x))
                preds.append((city, max(0.0, y_pred)))
            else:
                y_pred = float(y.mean()) if len(y) > 0 else 0.0
                preds.append((city, y_pred))

        pred_df = pd.DataFrame(preds, columns=["City", "Predicted_Quantity_Next_Month"]).sort_values(
            "Predicted_Quantity_Next_Month", ascending=False
        )

        st.subheader("📊 Prediction Results")
        st.dataframe(pred_df, use_container_width=True)
        download_df_button(pred_df, "Download CSV – Prediction", "prediction_next_month_by_city")

        # Highlight the top city clearly
        if not pred_df.empty:
            top_city = pred_df.iloc[0]["City"]
            top_qty = pred_df.iloc[0]["Predicted_Quantity_Next_Month"]
            st.success(f"🏆 **{top_city}** is predicted to have the highest available food next month (~ **{top_qty:.0f} units**).")


# ---------------------------------------------------
# CRUD Operations
# ---------------------------------------------------
with crud_tab:
    st.header("📝 Manage Food Data")
    action = st.selectbox("Choose an Action", ["Add", "Update", "Delete"])
    st.divider()

    if action == "Add":
        st.subheader("Add a New Food Listing")
        with st.form("add_food_form"):
            food_name = st.text_input("Food Name")
            food_type = st.selectbox("Food Type", options=["Vegan", "Non-Vegan", "Vegetarian", "Jain", "Gluten-Free"])
            meal_type = st.selectbox("Meal Type", options=["Breakfast", "Lunch", "Dinner", "Snack"])
            quantity = st.number_input("Quantity", min_value=1, step=1)
            provider_id = st.number_input("Provider ID", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date")
            location = st.text_input("Location (City)")
            submit_button = st.form_submit_button("Add Food Item")

            if submit_button:
                if food_name and food_type and meal_type and quantity and provider_id and location:
                    # Check if provider exists and get their type
                    ptype_df = run_query("SELECT Provider_Type FROM Providers WHERE Provider_ID=%s;", (provider_id,))
                    if not ptype_df.empty:
                        provider_type = ptype_df.iloc[0]["Provider_Type"]
                        q = """
                        INSERT INTO Food_Listings 
                        (Provider_ID, Food_Name, Food_Type, Meal_Type, Quantity, Expiry_Date, Location, Provider_Type)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """
                        params = (provider_id, food_name, food_type, meal_type, quantity, expiry_date, location, provider_type)
                        if execute_cud_query(q, params):
                            st.success("✅ Food item added successfully!")
                            st.cache_data.clear()  # Clear Streamlit cache to refresh queries
                        else:
                            st.error("❌ Failed to add food item. Check your database connection or data types.")
                    else:
                        st.error("❌ Invalid Provider ID. Please enter a valid ID from the Providers table.")
                else:
                    st.warning("⚠️ Please fill in all fields before submitting.")


# ---------------------------------------------------
# Learner SQL Queries
# ---------------------------------------------------
with learner_queries_tab:
    st.header("🧑‍💻 Learner SQL Queries")
    st.write("Write your own SQL query and see the results directly from the database.")

    # Text area for user to write the query
    user_query = st.text_area(
        "Write your SQL query:",
        placeholder="e.g., SELECT * FROM Providers LIMIT 10;",
        height=200
    )

    # Button to run the query
    if st.button("Run Query", use_container_width=True):
        if user_query:
            try:
                # Execute the user-provided query
                user_df = run_query(user_query)
                st.subheader("Query Results")
                st.dataframe(user_df, use_container_width=True)
                download_df_button(user_df, "Download Query Results", "user_query_results")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a query to run.")


# ---------------------------------------------------
# ABOUT
# ---------------------------------------------------
with about_tab:
    st.header(" About the Project")
    st.markdown("""
## **Project Objective**
To **minimize food wastage** by connecting **local food providers** (restaurants, grocery stores, bakeries, caterers, etc.) with **receivers** (NGOs, charities, individuals) using a **data-driven dashboard**.
The system tracks **food listings, claims, and donation trends** to make redistribution efficient and transparent.

---

## **Database Schema**
The project uses a **MySQL relational database** with the following tables:

1. **Providers**  
   `(Provider_ID, Name, Provider_Type, Address, City, Contact)`

2. **Receivers**  
   `(Receiver_ID, Name, Receiver_Type, City, Contact)`

3. **Food_Listings**  
   `(Food_ID, Provider_ID, Food_Name, Food_Type, Meal_Type, Quantity, Expiry_Date, Location, Provider_Type)`  
   > `Provider_Type` here is stored with each listing so we can directly filter/query food donations by type without extra joins.

4. **Claims**  
   `(Claim_ID, Food_ID, Receiver_ID, Timestamp, Status)`

---

## **Dataset**
- **Source:** Simulated dataset inspired by real-world food donation platforms.  
- **Entities:**
  - **Providers** – Food donors with details like name, type, city, and contact.
  - **Receivers** – Beneficiaries (NGOs/individuals) with city and contact info.
  - **Food Listings** – Items available for donation with type, meal, expiry, location, and provider type.
  - **Claims** – Requests from receivers with timestamps and completion status.

---

## **Tech Stack**
- **Frontend:** Streamlit (Python Web Framework)
- **Backend:** MySQL Database
- **Languages/Libraries:** Python, Pandas, NumPy, MySQL Connector
- **Visuals:** Streamlit native charts + interactive filtering
- **Prediction:** Lightweight Linear Regression on historical data

---

## **Key Features**
- **Interactive EDA** – bar charts, type breakdown, and claim status analysis.
- **15 curated SQL business queries** – grouped into Providers & Receivers, Food Listings, Claims, and Insights.
- **One-click CSV export** – for all query results.
- **Global filters** – City, Provider Type, and Meal Type applied across queries.
- **Prediction module** – estimates next month’s top city for available food.
- **CRUD Operations** – add, update, and delete food listings.

---

## **Impact & Real-World Relevance**
- Reduces **food wastage** by identifying surplus in specific regions.
- Helps **NGOs plan pickups** based on predicted availability.
- Promotes **sustainability** and **community engagement**.

---

## **Done By:**
- Manasvi Shetty  
- July 1 batch – Data Analytics  
- Email: manasvijain581@gmail.com  

---

## **How to Run Locally**
```bash
pip install streamlit pandas mysql-connector-python
streamlit run app.py
                """)