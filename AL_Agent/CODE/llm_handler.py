import requests
import re

# ✅ SQL generation for text queries
def get_sql_from_question(question):
    system_prompt = """
    You are a MySQL query generator.

    Your job is to take a user's question and convert it into a **valid MySQL query** using only the following table schemas:

    1. ad_sales_metrics(date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
    2. total_sales_metrics(date, item_id, total_sales, total_units_ordered)
    3. eligibility_table(eligibility_datetime_utc, item_id, eligibility, message)

    ⚠️ Rules:
    - Output ONLY the SQL code inside triple backticks like ```sql ... ```
    - NO explanations, NO comments, NO aliases unless necessary
    - NEVER guess column names — use only the ones above
    - Use built-in SQL functions like SUM(), AVG(), GROUP BY, etc.

    💡 Hints:
    - ROAS = SUM(ad_sales) / SUM(ad_spend)
    - CPC = SUM(ad_spend) / SUM(clicks)
    - Total Sales = SUM(total_sales)
    - Average Clicks per Day = AVG(clicks) GROUP BY date

    Carefully match fields to the correct table.
    """

    payload = {
        "model": "phi3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}. Only SQL."}
        ],
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=payload)
    response.raise_for_status()
    result = response.json()
    raw_response = (
        result.get("message", {}).get("content")
        or result.get("content")
        or result.get("response")
        or str(result)
    )

    sql_match = re.findall(r"```sql(.*?)```", raw_response, re.DOTALL)
    sql_query = sql_match[0].strip() if sql_match else "SELECT 1;"
    return sql_query


# ✅ SQL generation for graph-type questions
def get_sql_for_graph_question(question):
    system_prompt = """
    You are a MySQL SQL generator for data visualization.

    Given a user's question, generate a SQL query that returns grouped, aggregated data for plotting graphs.

    Use only these tables:
    1. ad_sales_metrics(date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
    2. total_sales_metrics(date, item_id, total_sales, total_units_ordered)
    3. eligibility_table(eligibility_datetime_utc, item_id, eligibility, message)

    Rules:
    - Output SQL inside triple backticks like ```sql ... ```
    - No explanation or comments.
    - Use GROUP BY date or item_id.
    - DO NOT use non-existent columns. Only use column names from above.

    Examples:
    - ROAS trend by date → SELECT date, SUM(ad_sales)/SUM(ad_spend) AS roas FROM ad_sales_metrics GROUP BY date
    - CPC by product → SELECT item_id, SUM(ad_spend)/SUM(clicks) AS cpc FROM ad_sales_metrics GROUP BY item_id
    """

    payload = {
        "model": "phi3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {question}. Return SQL only."}
        ],
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=payload)
    response.raise_for_status()
    result = response.json()
    raw_response = (
        result.get("message", {}).get("content")
        or result.get("content")
        or result.get("response")
        or str(result)
    )

    sql_match = re.findall(r"```sql(.*?)```", raw_response, re.DOTALL)
    sql_query = sql_match[0].strip() if sql_match else "SELECT 1;"
    return sql_query


# ✅ Explanation generation (unchanged)
def get_explanation_from_llm(sql_result, question):
    explanation_prompt = f"""
    You are a friendly assistant.

    Based on the SQL result below:
    {sql_result}

    Write a short and clear natural-language answer (max 3 lines) to the user's question:
    "{question}"

    Do NOT include SQL code. Just explain the result simply.
    """

    payload = {
        "model": "phi3",
        "messages": [
            {"role": "system", "content": "You explain SQL query results in human language."},
            {"role": "user", "content": explanation_prompt}
        ],
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=payload)
    response.raise_for_status()
    result = response.json()
    explanation = (
        result.get("message", {}).get("content")
        or result.get("content")
        or result.get("response")
        or str(result)
    ).strip()

    return explanation
