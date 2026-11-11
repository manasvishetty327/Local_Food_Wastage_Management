# Local Food Wastage Management

A data-driven application for exploring surplus food listings and claims, with the goal of supporting better food redistribution between providers and receivers.

## Project Overview

The project models a local food donation workflow. Food providers list available surplus food, receivers claim listings, and the application provides analysis of providers, food availability, and claim activity.

The application combines a Streamlit interface with a MySQL database and SQL-based analysis.

## Features

- **Dashboard overview** — display counts of providers, receivers, food listings, and claims.
- **Exploratory data analysis** — inspect provider distribution, food types, meal types, and claim status.
- **Business queries** — explore SQL questions about providers, receivers, listings, claims, and distribution.
- **Global filters** — filter supported analysis by city, provider type, and meal type.
- **CSV export** — download selected analysis and query results.
- **Prediction demonstration** — use a simple linear trend based on historical monthly food-listing quantities to estimate next-month availability by city.
- **Food listing entry** — add a food listing through the application interface.
- **Learner SQL workspace** — enter a SQL query and view its result in the dashboard.

## Technology Stack

| Area | Technologies |
|---|---|
| Language | Python |
| Dashboard | Streamlit |
| Data processing | Pandas, NumPy |
| Database | MySQL |
| Database connectivity | mysql-connector-python |
| Analysis | SQL |

## Database Design

The database is named `food_wastage_db2` and uses four main tables:

| Table | Purpose |
|---|---|
| `Providers` | Stores food provider details and location |
| `Receivers` | Stores receiver details and location |
| `Food_Listings` | Stores food items, quantities, expiry dates, and provider references |
| `Claims` | Tracks receiver claims and their status |

The schema and table definitions are available in [creating database and tables.sql](./creating%20database%20and%20tables.sql). Additional SQL files organise analysis queries for providers, listings, claims, and insights.

## Repository Contents

- `app.py` — Streamlit application
- `db_setup.py` — database setup helper
- `creating database and tables.sql` — database and table definitions
- `Food Providers & Receivers.sql` — provider and receiver queries
- `Food Listings & Availability.sql` — food listing queries
- `Claims & Distribution.sql` — claims and distribution queries
- `Analysis & Insights.sql` — analysis queries
- CSV files — sample provider, receiver, food listing, and claim datasets
- `requirements.txt` — Python dependencies

## Run Locally

### Prerequisites

- Python 3.10 or later
- MySQL Server
- Git

### 1. Clone the repository

```bash
git clone https://github.com/manasvishetty327/Local_Food_Wastage_Management.git
cd Local_Food_Wastage_Management
```

### 2. Create and activate a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the database

1. Start your local MySQL server.
2. Open `creating database and tables.sql` in MySQL Workbench or another MySQL client and execute it.
3. Load the supplied CSV data into the corresponding tables using your preferred import method.
4. Configure the connection using environment variables or Streamlit secrets.

**Windows PowerShell**

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_USER="your_mysql_user"
$env:MYSQL_PASSWORD="your_mysql_password"
$env:MYSQL_DATABASE="food_wastage_db2"
```

**macOS / Linux**

```bash
export MYSQL_HOST="localhost"
export MYSQL_USER="your_mysql_user"
export MYSQL_PASSWORD="your_mysql_password"
export MYSQL_DATABASE="food_wastage_db2"
```

Alternatively, create `.streamlit/secrets.toml` locally:

```toml
[mysql]
host = "localhost"
user = "your_mysql_user"
password = "your_mysql_password"
database = "food_wastage_db2"
```

Environment variables take precedence over Streamlit secrets. Keep `.streamlit/secrets.toml` out of version control and never commit real credentials.

### 5. Start the application

```bash
streamlit run app.py
```

Streamlit prints the local URL in the terminal (usually http://localhost:8501).

## Notes

- The prediction tab is a basic trend-based demonstration, not a production forecasting model.
- The application expects a configured MySQL database and populated tables to display meaningful results.
- The included CSV files provide the project data used for loading the database.

## Author

**Manasvi Shetty**
