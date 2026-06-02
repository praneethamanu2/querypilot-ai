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
    description="Safe Text-to-SQL Analytics Agent",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str


@app.on_event("startup")
def startup_event():
    """
    Creates the sample database when the API starts.
    """

    create_sample_database()


@app.get("/")
def home():
    return {
        "message": "InsightGuard AI API is running",
        "status": "healthy"
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
    2. Generate SQL.
    3. Validate SQL.
    4. Execute SQL.
    5. Run quality checks.
    6. Generate chart recommendation.
    7. Generate business insight.
    8. Log query event.
    9. Return all results.
    """

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    generated = generate_sql_from_question(request.question)
    intent = generated["intent"]
    sql_query = generated["sql_query"]

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

    try:
        dataframe = execute_sql_query(sql_query)
        row_count = len(dataframe)

        quality_checks = run_result_quality_checks(dataframe)
        chart_type = recommend_chart_type(intent)
        insight = generate_business_insight(dataframe, intent)
        sql_explanation = explain_generated_sql(intent)

        log_query_event(
            question=request.question,
            sql_query=sql_query,
            status="success",
            row_count=row_count
        )

        return {
            "question": request.question,
            "intent": intent,
            "sql_query": sql_query,
            "sql_explanation": sql_explanation,
            "validation_message": validation["message"],
            "row_count": row_count,
            "columns": list(dataframe.columns),
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