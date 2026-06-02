import requests
import pandas as pd
import plotly.express as px
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8001"


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="QueryPilot AI",
    page_icon="🚀",
    layout="wide"
)


# -----------------------------
# Theme-Friendly CSS
# -----------------------------
st.markdown(
    """
    <style>
    /* Make Streamlit top toolbar blend with selected theme */
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

    /* Main app background follows Streamlit theme */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Main title */
    .main-title {
        font-size: 48px;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        letter-spacing: -1px;
    }

    /* Subtitle */
    .subtitle {
        font-size: 21px;
        color: var(--text-color);
        opacity: 0.85;
        margin-top: 0px;
        margin-bottom: 24px;
        font-weight: 500;
    }

    /* Info box */
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

    /* Success box */
    .success-box {
        background-color: rgba(16, 185, 129, 0.12);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-left: 6px solid #10b981;
        color: var(--text-color);
        margin-top: 12px;
    }

    /* Helper text */
    .small-text {
        color: var(--text-color);
        opacity: 0.65;
        font-size: 14px;
        padding-top: 8px;
    }

    /* Text area / query box */
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

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border-color: rgba(148, 163, 184, 0.45) !important;
    }

    /* Button */
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

    /* Metric cards */
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

    /* Tabs */
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

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-color);
    }

    /* Dividers */
    hr {
        border-color: rgba(148, 163, 184, 0.2);
    }

    /* Headings */
    h1, h2, h3 {
        color: var(--text-color);
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    "<div class='main-title'>QueryPilot AI</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Safe Text-to-SQL Analytics Assistant</div>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class='info-box'>
    <b>What this app does:</b><br>
    QueryPilot AI lets users ask business questions in plain English, safely converts them into SQL,
    validates the query, runs it on the database, and returns tables, charts, and business insights.
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("📌 Project Guide")

    st.markdown(
        """
        QueryPilot AI demonstrates:

        - Natural language analytics
        - SQL generation
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
        "Show discount analysis by region."
    ]

    selected_example = st.selectbox(
        "Choose a question",
        [""] + example_questions
    )

    st.divider()

    st.subheader("Governance Rules")

    try:
        rules_response = requests.get(f"{API_BASE_URL}/governance-rules")

        if rules_response.status_code == 200:
            rules = rules_response.json()["rules"]

            for rule in rules:
                st.write(f"✅ {rule}")
        else:
            st.warning("Could not load governance rules.")

    except requests.exceptions.ConnectionError:
        st.error("Backend is not connected.")


# -----------------------------
# Question Input Section
# -----------------------------
st.subheader("Ask a Business Question")

default_question = selected_example if selected_example else ""

question = st.text_area(
    label="Type your question below",
    value=default_question,
    height=120,
    placeholder="Example: What is revenue by region?"
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


# -----------------------------
# Function: Create Chart
# -----------------------------
def create_chart(dataframe, chart_type):
    """
    Creates a chart based on the chart type returned by the backend.
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


# -----------------------------
# Main Analysis Logic
# -----------------------------
if analyze_button:
    if not question.strip():
        st.error("Please enter a business question.")

    else:
        try:
            with st.spinner("Generating SQL, validating safety, running query, and preparing insights..."):
                response = requests.post(
                    f"{API_BASE_URL}/ask",
                    json={"question": question}
                )

            if response.status_code == 200:
                result = response.json()
                dataframe = pd.DataFrame(result["data"])

                st.divider()

                # Summary Metrics
                st.subheader("Analysis Summary")

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                with metric_col1:
                    st.metric(
                        label="Detected Intent",
                        value=result["intent"].replace("_", " ").title()
                    )

                with metric_col2:
                    st.metric(
                        label="Rows Returned",
                        value=result["row_count"]
                    )

                with metric_col3:
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

                # Business Insight
                st.subheader("Business Insight")
                st.info(result["insight"])

                # Output Tabs
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

                with tab5:
                    try:
                        history_response = requests.get(f"{API_BASE_URL}/history")

                        if history_response.status_code == 200:
                            history = history_response.json()["history"]

                            if history:
                                history_df = pd.DataFrame(history)
                                st.dataframe(history_df, use_container_width=True)
                            else:
                                st.info("No query history yet.")

                    except requests.exceptions.ConnectionError:
                        st.warning("Query history unavailable because backend is not connected.")

            else:
                try:
                    error_detail = response.json()["detail"]
                except Exception:
                    error_detail = response.text

                st.error(error_detail)

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the FastAPI backend. Make sure the backend is running on port 8001."
            )


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.markdown(
    """
    <p class='small-text'>
    QueryPilot AI was built with Python, FastAPI, Streamlit, SQLite, Pandas, Plotly, and SQL validation logic.
    </p>
    """,
    unsafe_allow_html=True
)