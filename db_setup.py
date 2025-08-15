import pandas as pd
import mysql.connector

# Step 1 – Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",             # change if your MySQL username is different
    password="root"          # change to your MySQL password
)
cursor = conn.cursor()

# Step 2 – Create new database
cursor.execute("CREATE DATABASE IF NOT EXISTS food_wastage_db2")
cursor.execute("USE food_wastage_db2")

# Step 3 – Drop existing tables (so script can re-run without errors)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("DROP TABLE IF EXISTS Claims")
cursor.execute("DROP TABLE IF EXISTS Food_Listings")
cursor.execute("DROP TABLE IF EXISTS Receivers")
cursor.execute("DROP TABLE IF EXISTS Providers")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Step 4 – Create tables with updated column names
cursor.execute("""
CREATE TABLE Providers (
    Provider_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Provider_Type VARCHAR(50),   -- changed from Type to match CSV
    Address VARCHAR(200),
    City VARCHAR(50),
    Contact VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE Receivers (
    Receiver_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100),
    Provider_Type VARCHAR(50),   -- matches CSV
    City VARCHAR(50),
    Contact VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE Food_Listings (
    Food_ID INT PRIMARY KEY AUTO_INCREMENT,
    Food_Name VARCHAR(100),
    Quantity INT,
    Expiry_Date DATE,
    Provider_ID INT,
    Provider_Type VARCHAR(50),
    Location VARCHAR(50),
    Food_Type VARCHAR(50),
    Meal_Type VARCHAR(50),
    FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID)
)
""")

cursor.execute("""
CREATE TABLE Claims (
    Claim_ID INT PRIMARY KEY AUTO_INCREMENT,
    Food_ID INT,
    Receiver_ID INT,
    Status VARCHAR(50),
    Timestamp DATETIME,
    FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID),
    FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID)
)
""")

# Step 5 – Insert CSV data
csv_files = {
    "Providers": "datasets/providers_data.csv",
    "Receivers": "datasets/receivers_data.csv",
    "Food_Listings": "datasets/food_listings_data.csv",
    "Claims": "datasets/claims_data.csv"
}

for table, file in csv_files.items():
    df = pd.read_csv(file)

    # Data cleaning
    df.drop_duplicates(inplace=True)
    df.fillna("N/A", inplace=True)

    # Convert date columns if they exist
    if "Expiry_Date" in df.columns:
        df["Expiry_Date"] = pd.to_datetime(df["Expiry_Date"], errors="coerce").dt.date
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Ensure Contact values don't break DB length
    if "Contact" in df.columns:
        df["Contact"] = df["Contact"].astype(str).str[:100]

    # Insert rows into MySQL
    for _, row in df.iterrows():
        cols = ", ".join(df.columns)
        vals = ", ".join(["%s"] * len(df.columns))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
        cursor.execute(sql, tuple(row))

conn.commit()
conn.close()

print("✅ Database and tables created, CSV data inserted successfully!")
