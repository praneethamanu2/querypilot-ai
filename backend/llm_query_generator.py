import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from backend.database import get_database_schema


load_dotenv()


def generate_sql_with_llm(question: str) -> dict:
    """
    Uses an LLM to generate a SQLite SELECT query from a natural language question.

    Important:
    The LLM only generates SQL.
    The generated SQL still goes through sql_validator.py before execution.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    if not api_key:
        return {
            "intent": "missing_api_key",
            "sql_query": "",
            "sql_explanation": (
                "OPENAI_API_KEY is missing. Add your API key to a .env file "
                "or use Rule-based mode instead."
            )
        }

    client = OpenAI(api_key=api_key)

    schema = get_database_schema()

    system_prompt = f"""
You are a careful Text-to-SQL assistant for a business analytics app.

Your task:
Convert a user's business question into a valid SQLite SELECT query.

Database schema:
{schema}

Strict rules:
1. Generate only read-only SELECT queries.
2. Use only these tables: customers, products, orders.
3. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, ATTACH, or DETACH.
4. Use valid SQLite syntax.
5. Do not invent tables or columns.
6. Keep the query simple and readable.
7. Return only valid JSON.
8. Do not include markdown or code fences.

Return JSON in exactly this format:
{{
  "intent": "short_snake_case_intent",
  "sql_query": "SELECT ...",
  "sql_explanation": "Plain English explanation of what the SQL does."
}}
"""

    user_prompt = f"""
Business question:
{question}
"""

    try:
        response = client.responses.create(
            model=model_name,
            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        raw_output = response.output_text.strip()

        parsed_output = json.loads(raw_output)

        return {
            "intent": parsed_output.get("intent", "llm_generated_query"),
            "sql_query": parsed_output.get("sql_query", "").strip(),
            "sql_explanation": parsed_output.get(
                "sql_explanation",
                "This SQL query was generated from the business question."
            )
        }

    except json.JSONDecodeError:
        return {
            "intent": "llm_json_parse_error",
            "sql_query": "",
            "sql_explanation": (
                "The LLM response was not valid JSON. Try rephrasing the question "
                "or use Rule-based mode."
            )
        }

    except Exception as error:
        return {
            "intent": "llm_error",
            "sql_query": "",
            "sql_explanation": f"LLM generation failed: {str(error)}"
        }