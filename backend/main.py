from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.database import (
    create_sample_database,
    execute_sql_query,
    get_database_schema
)
from backend.query_generator import (
    generate_sql_from_question,
    explain_generated_sql
)
from backend.llm_query_generator import generate_sql_with_llm
from backend.sql_validator import (
    validate_sql_query,
    get_governance_rules
)
from backend.insight_generator import (
    generate_business_insight,
    run_result_quality_checks
)
from backend.chart_recommender import recommend_chart_type
from backend.audit_logger import log_query_event, read_query_history


app = FastAPI(
    title="QueryPilot AI API",
    description="Safe Text-to-SQL Analytics Assistant",
    version="2.0.0"
)


class QuestionRequest(BaseModel):
    question: str
    mode: str = "rule"


@app.on_event("startup")
def startup_event():
    """
    Creates the sample database when the API starts.
    """

    create_sample_database()


@app.get("/")
def home():
    return {
        "message": "QueryPilot AI API is running",
        "status": "healthy",
        "version": "2.0.0",
        "modes": ["rule", "llm"]
    }


@app.get("/schema")
def schema():
    """
    Returns database schema.
    """

    return {
        "schema": get_database_schema()
    }


@app.get("/governance-rules")
def governance_rules():
    """
    Returns safety rules used by the app.
    """

    return {
        "rules": get_governance_rules()
    }


@app.get("/history")
def history():
    """
    Returns recent query history.
    """

    return {
        "history": read_query_history()
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Main endpoint.

    Flow:
    1. Receive business question.
    2. Generate SQL using rule-based mode or LLM-powered mode.
    3. Validate SQL.
    4. Execute SQL.
    5. Run quality checks.
    6. Recommend chart type.
    7. Generate business insight.
    8. Log query event.
    9. Return all results.
    """

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    mode = request.mode.lower().strip()

    if mode not in ["rule", "llm"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Use 'rule' or 'llm'."
        )

    # -----------------------------
    # SQL Generation
    # -----------------------------
    if mode == "llm":
        generated = generate_sql_with_llm(request.question)
        intent = generated["intent"]
        sql_query = generated["sql_query"]
        sql_explanation = generated["sql_explanation"]
        generation_mode = "LLM-powered"
    else:
        generated = generate_sql_from_question(request.question)
        intent = generated["intent"]
        sql_query = generated["sql_query"]
        sql_explanation = explain_generated_sql(intent)
        generation_mode = "Rule-based"

    if not sql_query.strip():
        log_query_event(
            question=request.question,
            sql_query=sql_query,
            status="generation_failed",
            row_count=0
        )

        raise HTTPException(
            status_code=400,
            detail=sql_explanation
        )

    # -----------------------------
    # SQL Safety Validation
    # -----------------------------
    validation = validate_sql_query(sql_query)

    if not validation["is_valid"]:
        log_query_event(
            question=request.question,
            sql_query=sql_query,
            status="blocked",
            row_count=0
        )

        raise HTTPException(
            status_code=400,
            detail=validation["message"]
        )

    # -----------------------------
    # Query Execution
    # -----------------------------
    try:
        dataframe = execute_sql_query(sql_query)
        row_count = len(dataframe)
        columns = list(dataframe.columns)

        quality_checks = run_result_quality_checks(dataframe)
        chart_type = recommend_chart_type(intent, columns)
        insight = generate_business_insight(dataframe, intent)

        log_query_event(
            question=request.question,
            sql_query=sql_query,
            status="success",
            row_count=row_count
        )

        return {
            "question": request.question,
            "generation_mode": generation_mode,
            "intent": intent,
            "sql_query": sql_query,
            "sql_explanation": sql_explanation,
            "validation_message": validation["message"],
            "row_count": row_count,
            "columns": columns,
            "data": dataframe.to_dict(orient="records"),
            "chart_type": chart_type,
            "insight": insight,
            "quality_checks": quality_checks
        }

    except Exception as error:
        log_query_event(
            question=request.question,
            sql_query=sql_query,
            status="failed",
            row_count=0
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )