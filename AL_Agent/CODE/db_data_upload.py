import pandas as pd
import mysql.connector

# ✅ Database connection details
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Heiswithme2034",  
    database="ecommerce_db"
)

cursor = conn.cursor()

# ✅ DATASET 1: AD SALES METRICS
df_ad = pd.read_csv("Data/Product-Level Ad Sales and Metrics (mapped) - Product-Level Ad Sales and Metrics (mapped).csv")

for index, row in df_ad.iterrows():
    cursor.execute("""
        INSERT INTO ad_sales_metrics (date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))
conn.commit()
print("✅ Ad Sales Data Uploaded.")

# ✅ DATASET 2: TOTAL SALES METRICS
df_total = pd.read_csv("Data/Product-Level Total Sales and Metrics (mapped) - Product-Level Total Sales and Metrics (mapped).csv")

for index, row in df_total.iterrows():
    cursor.execute("""
        INSERT INTO total_sales_metrics (date, item_id, total_sales, total_units_ordered)
        VALUES (%s, %s, %s, %s)
    """, tuple(row))
conn.commit()
print("✅ Total Sales Data Uploaded.")

# ✅ DATASET 3: ELIGIBILITY TABLE with NaN Handling
df_eligibility = pd.read_csv("Data/Product-Level Eligibility Table (mapped) - Product-Level Eligibility Table (mapped).csv")

for index, row in df_eligibility.iterrows():
    values = (
        row['eligibility_datetime_utc'],
        row['item_id'],
        row['eligibility'],
        None if pd.isna(row['message']) else row['message']
    )
    cursor.execute("""
        INSERT INTO eligibility_table (eligibility_datetime_utc, item_id, eligibility, message)
        VALUES (%s, %s, %s, %s)
    """, values)
conn.commit()
print("✅ Eligibility Data Uploaded.")

# ✅ Close connection
cursor.close()
conn.close()
print("✅✅ All Data Uploaded Successfully!")
