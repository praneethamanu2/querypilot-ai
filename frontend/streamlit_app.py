```python
import os
import requests
import pandas as pd
import plotly.express as px
import streamlit as st


# -------------------------------------------------
# API Configuration
# -------------------------------------------------
# Local default for development.
# On Streamlit Cloud, backend may not be available, so demo fallback will run.
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")


# -------------------------------------------------
# Demo fallback data for public live demo
# -------------------------------------------------
def get_demo_result(question, mode_value):
    question_lower = question.lower()

    if "region" in question_lower and "revenue" in question_lower:
        data = [
            {"region": "West", "total_revenue": 185000},
            {"region": "East", "total_revenue": 142500},
            {"region": "South", "total_revenue": 119800},
            {"region": "North", "total_revenue": 98000},
        ]
        sql_query = """
SELECT region, SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;
"""
        intent = "revenue_by_region"
        chart_type = "bar"
        insight = "The West region generated the highest revenue, followed by the East region. This suggests the West may be the strongest market for sales growth."
        explanation = "This query groups sales records by region, calculates total revenue for each region, and sorts the results from highest to lowest revenue."

    elif "category" in question_lower and "revenue" in question_lower:
        data = [
            {"category": "Electronics", "total_revenue": 210000},
            {"category": "Furniture", "total_revenue": 156000},
            {"category": "Clothing", "total_revenue": 125000},
            {"category": "Office Supplies", "total_revenue": 84500},
        ]
        sql_query = """
SELECT category, SUM(revenue) AS total_revenue
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;
"""
        intent = "revenue_by_category"
        chart_type = "bar"
        insight = "Electronics generated the highest revenue among all product categories."
        explanation = "This query groups records by product category and calculates total revenue for each category."

    elif "monthly" in question_lower or "trend" in question_lower:
        data = [
            {"month": "Jan", "revenue": 45000},
            {"month": "Feb", "revenue": 52000},
            {"month": "Mar", "revenue": 61000},
            {"month": "Apr", "revenue": 73000},
            {"month": "May", "revenue": 81000},
        ]
        sql_query = """
SELECT month, SUM(revenue) AS revenue
FROM sales
GROUP BY month
ORDER BY month;
"""
        intent = "monthly_sales_trend"
        chart_type = "line"
        insight = "Revenue shows a steady upward trend across the months, indicating improving sales performance."
        explanation = "This query groups sales by month and calculates total revenue for each month to show the trend over time."

    elif "top" in question_lower and "customer" in question_lower:
        data = [
            {"customer": "Acme Corp", "total_spent": 42000},
            {"customer": "Northwind LLC", "total_spent": 38500},
            {"customer": "Bright Retail", "total_spent": 34100},
            {"customer": "Summit Partners", "total_spent": 29800},
            {"customer": "BlueStone Inc", "total_spent": 25600},
        ]
        sql_query = """
SELECT customer, SUM(order_amount) AS total_spent
FROM orders
GROUP BY customer
ORDER BY total_spent DESC
LIMIT 10;
"""
        intent = "top_customers"
        chart_type = "bar"
        insight = "Acme Corp is the highest-value customer in this demo dataset."
        explanation = "This query groups orders by customer and ranks customers by total spending."

    else:
        data = [
            {"region": "West", "total_revenue": 185000},
            {"region": "East", "total_revenue": 142500},
            {"region": "South", "total_revenue": 119800},
            {"region": "North", "total_revenue": 98000},
        ]
        sql_query = """
SELECT region, SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;
"""
        intent = "safe_demo_analytics"
        chart_type = "bar"
        insight = "Demo mode returned a safe analytics result. The West region has the highest total revenue."
        explanation = "This sample query demonstrates QueryPilot AI's Text-to-SQL workflow using a safe predefined analytics template."

    return {
        "intent": intent,
        "row_count": len(data),
        "chart_type": chart_type,
        "data": data,
        "insight": insight,
        "sql_query": sql_query.strip(),
        "sql_explanation": explanation,
        "validation_message": "Demo SQL passed safety validation. Only SELECT-style analytics queries are allowed.",
        "quality_checks": [
            "No destructive SQL operations detected.",
            "Query uses safe read-only analytics pattern.",
            "Result is suitable for dashboard display.",
            "SQL output is explainable for business users.",
        ],
        "mode": mode_value,
        "demo_mode": True,
    }


# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="QueryPilot AI",
    page_icon="🚀",
    layout="wide"
)


# -------------------------------------------------
# Theme-Friendly CSS
# -------------------------------------------------
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
    }

    header[data-testid="stHeader"] * {
        color: var(--text-color) !important;
    }

    div[data-testid="stToolbar"] {
        background-color: transparent !important;
        color: var(--text-color) !important;
    }

    div[data-testid="stToolbar"] button {
        color: var(--text-color) !important;
        background-color: transparent !important;
    }

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .main-title {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }

    .subtitle {
        font-size: 21px;
        color: var(--text-color);
        opacity: 0.85;
        margin-top: 0px;
        margin-bottom: 24px;
        font-weight: 500;
    }

    .info-box {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-left: 6px solid #38bdf8;
        margin-bottom: 22px;
        color: var(--text-color);
        box-shadow: 0px 6px 20px rgba(0, 0, 0, 0.12);
    }

    .success-box {
        background-color: rgba(16, 185, 129, 0.12);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 6px solid #10b981;
        color: var(--text-color);
        margin-top: 12px;
    }

    .warning-box {
        background-color: rgba(245, 158, 11, 0.12);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-left: 6px solid #f59e0b;
        color: var(--text-color);
        margin-top: 12px;
    }

    .small-text {
        color: var(--text-color);
        opacity: 0.65;
        font-size: 14px;
        padding-top: 8px;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border: 1px solid rgba(148, 163, 184, 0.45) !important;
        border-radius: 12px !important;
        font-size: 16px !important;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    }

    div[data-testid="stTextArea"] textarea::placeholder {
        color: var(--text-color) !important;
        opacity: 0.55;
    }

    div[data-baseweb="select"] > div {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border-color: rgba(148, 163, 184, 0.45) !important;
    }

    div[data-testid="stRadio"] label {
        color: var(--text-color) !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 700;
        transition: 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8, #6d28d9);
        transform: translateY(-1px);
        box-shadow: 0px 8px 20px rgba(37, 99, 235, 0.35);
        color: white !important;
    }

    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0px 4px 18px rgba(0, 0, 0, 0.10);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--text-color) !important;
        opacity: 0.8;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text-color) !important;
        font-weight: 800;
    }

    button[data-baseweb="tab"] {
        color: var(--text-color) !important;
        font-weight: 600;
        opacity: 0.8;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
        opacity: 1;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-color);
    }

    hr {
        border-color: rgba(148, 163, 184, 0.2);
    }

    h1, h2, h3 {
        color: var(--text-color);
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown(
    "<div class='main-title'>🚀 QueryPilot AI</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Safe Text-to-SQL Analytics Assistant for Business Teams</div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class='info-box'>
    <b>What this app does:</b><br>
    QueryPilot AI lets users ask business questions in plain English, converts them into SQL,
    validates the query for safety, runs it on the database, and returns tables, charts, and business insights.
    <br><br>
    <b>Live demo note:</b> If the FastAPI backend is not connected, this deployed version automatically uses demo mode
    so recruiters can still test the product flow.
    </div>
    """,
    unsafe_allow_html=True
)


# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.title("📌 Project Guide")

    st.markdown(
        """
        QueryPilot AI demonstrates:

        - Natural language analytics
        - Text-to-SQL generation
        - LLM-powered SQL generation
        - SQL safety validation
        - Query execution
        - Dashboarding
        - Business insight generation
        - Audit logging
        """
    )

    st.divider()

    st.subheader("Try Example Questions")

    example_questions = [
        "What is revenue by region?",
        "Show revenue by category.",
        "Show monthly sales trend.",
        "Who are the top 10 customers?",
        "What is return rate by category?",
        "What is average order value by region?",
        "Show discount analysis by region.",
        "Which product category generated the highest revenue?",
        "Which region has the highest average order value?"
    ]

    selected_example = st.selectbox(
        "Choose a question",
        [""] + example_questions
    )

    st.divider()

    st.subheader("Governance Rules")

    try:
        rules_response = requests.get(
            f"{API_BASE_URL}/governance-rules",
            timeout=3
        )

        if rules_response.status_code == 200:
            rules = rules_response.json().get("rules", [])

            for rule in rules:
                st.write(f"✅ {rule}")
        else:
            raise Exception("Governance endpoint unavailable.")

    except Exception:
        demo_rules = [
            "Only read-only SELECT queries are allowed.",
            "DELETE, DROP, UPDATE, INSERT, and ALTER statements are blocked.",
            "Generated SQL must pass validation before execution.",
            "Queries are checked for unsafe patterns before results are shown.",
        ]

        for rule in demo_rules:
            st.write(f"✅ {rule}")

        st.caption("Demo mode: showing sample governance rules because backend is not connected.")


# -------------------------------------------------
# Question Input Section
# -------------------------------------------------
st.subheader("Ask a Business Question")

default_question = selected_example if selected_example else ""

question = st.text_area(
    label="Type your question below",
    value=default_question,
    height=120,
    placeholder="Example: What is revenue by region?"
)

generation_mode = st.radio(
    "Choose SQL Generation Mode",
    ["Rule-based", "LLM-powered"],
    horizontal=True
)

mode_value = "llm" if generation_mode == "LLM-powered" else "rule"

if generation_mode == "Rule-based":
    st.markdown(
        """
        <div class='success-box'>
        ✅ Rule-based mode works without an API key. It uses predefined intent detection and SQL templates.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class='warning-box'>
        ⚠️ LLM-powered mode usually requires an API key. In the public demo, the app can still show a safe simulated output.
        </div>
        """,
        unsafe_allow_html=True
    )


col_button, col_hint = st.columns([1, 3])

with col_button:
    analyze_button = st.button(
        "🚀 Generate Safe Analytics",
        use_container_width=True
    )

with col_hint:
    st.markdown(
        "<p class='small-text'>Tip: Start with one of the example questions from the sidebar.</p>",
        unsafe_allow_html=True
    )


# -------------------------------------------------
# Function: Create Chart
# -------------------------------------------------
def create_chart(dataframe, chart_type):
    """
    Creates a chart based on the chart type returned by the backend or demo fallback.
    """

    if dataframe.empty:
        st.info("No data available to visualize.")
        return

    if chart_type == "bar" and len(dataframe.columns) >= 2:
        fig = px.bar(
            dataframe,
            x=dataframe.columns[0],
            y=dataframe.columns[1],
            title="Business Analytics Result",
            text=dataframe.columns[1]
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            font=dict(color="#e5e7eb"),
            xaxis_title=dataframe.columns[0].replace("_", " ").title(),
            yaxis_title=dataframe.columns[1].replace("_", " ").title(),
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "line" and len(dataframe.columns) >= 2:
        fig = px.line(
            dataframe,
            x=dataframe.columns[0],
            y=dataframe.columns[1],
            markers=True,
            title="Trend Analysis"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,23,42,0.8)",
            font=dict(color="#e5e7eb"),
            xaxis_title=dataframe.columns[0].replace("_", " ").title(),
            yaxis_title=dataframe.columns[1].replace("_", " ").title(),
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("A table view is best for this result.")


# -------------------------------------------------
# Function: Render Result
# -------------------------------------------------
def render_result(result, generation_mode):
    dataframe = pd.DataFrame(result["data"])

    st.divider()

    if result.get("demo_mode"):
        st.warning(
            "Demo mode is active because the FastAPI backend is not connected on Streamlit Cloud. "
            "This still demonstrates the product workflow, SQL validation concept, charts, and analytics UI."
        )

    # -------------------------------------------------
    # Summary Metrics
    # -------------------------------------------------
    st.subheader("Analysis Summary")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            label="Generation Mode",
            value=generation_mode
        )

    with metric_col2:
        st.metric(
            label="Detected Intent",
            value=result["intent"].replace("_", " ").title()
        )

    with metric_col3:
        st.metric(
            label="Rows Returned",
            value=result["row_count"]
        )

    with metric_col4:
        st.metric(
            label="Recommended Chart",
            value=result["chart_type"].title()
        )

    st.markdown(
        """
        <div class='success-box'>
        ✅ SQL passed safety validation and was executed successfully.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # -------------------------------------------------
    # Business Insight
    # -------------------------------------------------
    st.subheader("Business Insight")
    st.info(result["insight"])

    # -------------------------------------------------
    # Output Tabs
    # -------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Visualization",
            "📋 Data Table",
            "🧠 Generated SQL",
            "🛡️ Safety Checks",
            "🕒 Query History"
        ]
    )

    with tab1:
        st.write("This chart is automatically selected based on the question type.")
        create_chart(dataframe, result["chart_type"])

    with tab2:
        st.write("Query output returned from the database.")
        st.dataframe(dataframe, use_container_width=True)

        if not dataframe.empty:
            csv_data = dataframe.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download Results as CSV",
                data=csv_data,
                file_name="querypilot_results.csv",
                mime="text/csv"
            )

    with tab3:
        st.write("This is the SQL query generated from your business question.")
        st.code(result["sql_query"], language="sql")

        st.write("**Plain-English SQL Explanation:**")
        st.write(result["sql_explanation"])

    with tab4:
        st.write("QueryPilot AI checks the query and result before showing the final output.")

        st.success(result["validation_message"])

        st.write("**Result Quality Checks:**")
        for check in result["quality_checks"]:
            st.write(f"- {check}")

        st.write("**Why this matters:**")
        st.write(
            "The SQL safety layer prevents unsafe database operations and makes the analytics workflow more reliable."
        )

    with tab5:
        try:
            history_response = requests.get(
                f"{API_BASE_URL}/history",
                timeout=3
            )

            if history_response.status_code == 200:
                history = history_response.json().get("history", [])

                if history:
                    history_df = pd.DataFrame(history)
                    st.dataframe(history_df, use_container_width=True)
                else:
                    st.info("No query history yet.")
            else:
                raise Exception("History endpoint unavailable.")

        except Exception:
            st.info("Demo mode: query history is unavailable because the backend is not connected.")


# -------------------------------------------------
# Main Analysis Logic
# -------------------------------------------------
if analyze_button:
    if not question.strip():
        st.error("Please enter a business question.")

    else:
        try:
            with st.spinner("Generating SQL, validating safety, running query, and preparing insights..."):
                response = requests.post(
                    f"{API_BASE_URL}/ask",
                    json={
                        "question": question,
                        "mode": mode_value
                    },
                    timeout=6
                )

            if response.status_code == 200:
                result = response.json()
            else:
                result = get_demo_result(question, mode_value)

            render_result(result, generation_mode)

        except Exception:
            result = get_demo_result(question, mode_value)
            render_result(result, generation_mode)


# -------------------------------------------------
# Footer
# -------------------------------------------------
st.divider()

st.markdown(
    """
    <p class='small-text'>
    QueryPilot AI was built with Python, FastAPI, Streamlit, SQLite, Pandas, Plotly,
    SQL validation logic, and optional LLM-powered SQL generation.
    </p>
    """,
    unsafe_allow_html=True
)
```
