from fastapi import FastAPI
from fastapi.responses import FileResponse
import mysql.connector
from llm_handler import get_sql_from_question, get_sql_for_graph_question, get_explanation_from_llm
import plotly.graph_objects as go
import pandas as pd
import os

app = FastAPI()

# ✅ Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Heiswithme2034",
    database="ecommerce_db"
)
cursor = conn.cursor()

# ✅ Endpoint: /query - Text-based SQL answers
@app.get("/query/")
def read_query(question: str):
    sql_query = get_sql_from_question(question)
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if not result:
            answer = "I couldn't find any matching data for your question."
        else:
            df = pd.DataFrame(result, columns=columns)
            result_for_llm = df.head(10).to_string(index=False)
            answer = get_explanation_from_llm(result_for_llm, question)
            print("✅ LLM Answer:", answer)

        return {
            "answer": answer or "⚠️ No answer received from LLM.",
            "sql_query": sql_query  # Optional: expose for debugging
        }

    except Exception as e:
        return {"error": str(e), "sql_query": sql_query}

# ✅ Endpoint: /graph - Visual questions
@app.get("/graph/")
def generate_graph(question: str):
    sql_query = get_sql_for_graph_question(question)
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        print(f"✅ Executed SQL: {sql_query}")
        print(f"✅ Columns Returned: {columns}")

        # ✅ Generate plot
        if "date" in df.columns:
            y_col = [col for col in df.columns if col != "date"][0]
            fig = go.Figure(data=go.Scatter(x=df["date"], y=df[y_col], mode="lines+markers"))
        else:
            x_col, y_col = df.columns[0], df.columns[1]
            fig = go.Figure(data=go.Bar(x=df[x_col], y=df[y_col]))

        fig.update_layout(title=question)
        fig.write_image("output_graph.png")

        # ✅ Generate explanation
        result_for_llm = df.head(10).to_string(index=False)
        explanation = get_explanation_from_llm(result_for_llm, question)
        print("✅ LLM Graph Insight:", explanation)

        return {
            "message": explanation or "⚠️ Could not interpret graph result",
            "graph_path": os.path.abspath("output_graph.png"),
            "sql_query": sql_query  # Optional for dev
        }

    except Exception as e:
        return {"error": str(e), "sql_query": sql_query}
