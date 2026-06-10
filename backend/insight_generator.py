import pandas as pd


def generate_business_insight(dataframe: pd.DataFrame, intent: str) -> str:
    """
    Generates a simple business insight from query results.

    Works for both:
    1. Rule-based queries
    2. LLM-generated queries
    """

    if dataframe.empty:
        return "No data was returned for this question. Try asking a broader question."

    if intent in ["revenue_by_region", "revenue_by_category"]:
        top_row = dataframe.iloc[0]
        first_col = dataframe.columns[0]
        value_col = dataframe.columns[1]

        return (
            f"The highest performing {first_col.replace('_', ' ')} is "
            f"{top_row[first_col]} with {top_row[value_col]} in total revenue."
        )

    if intent == "monthly_revenue_trend":
        max_row = dataframe.loc[dataframe["total_revenue"].idxmax()]
        return (
            f"The strongest revenue month was {max_row['month']} "
            f"with total revenue of {max_row['total_revenue']}."
        )

    if intent == "top_customers":
        top_customer = dataframe.iloc[0]
        return (
            f"The top customer is {top_customer['customer_name']} from "
            f"{top_customer['region']} with total revenue of {top_customer['total_revenue']}."
        )

    if intent == "return_rate_by_category":
        top_return = dataframe.iloc[0]
        return (
            f"The category with the highest return rate is {top_return['category']} "
            f"at {top_return['return_rate_percent']}%."
        )

    if intent == "average_order_value_by_region":
        top_region = dataframe.iloc[0]
        return (
            f"The region with the highest average order value is {top_region['region']} "
            f"with an average order value of {top_region['average_order_value']}."
        )

    if intent == "discount_analysis":
        top_discount = dataframe.iloc[0]
        return (
            f"The region with the highest average discount is {top_discount['region']} "
            f"at {top_discount['average_discount_percent']}%."
        )

    # Generic insight for LLM-generated queries
    if len(dataframe.columns) >= 2:
        first_col = dataframe.columns[0]
        second_col = dataframe.columns[1]

        try:
            top_row = dataframe.iloc[0]
            return (
                f"The top result is {top_row[first_col]} with "
                f"{second_col.replace('_', ' ')} of {top_row[second_col]}."
            )
        except Exception:
            return "The query was executed successfully. Review the table and chart for insights."

    return "The query was executed successfully. Review the table output for business insights."


def run_result_quality_checks(dataframe: pd.DataFrame) -> list:
    """
    Checks result quality before showing insights.
    """

    checks = []

    if dataframe.empty:
        checks.append("Warning: Query returned no rows.")
        return checks

    missing_values = dataframe.isnull().sum().sum()

    if missing_values > 0:
        checks.append(f"Warning: Result contains {missing_values} missing values.")

    if len(dataframe) > 1000:
        checks.append("Warning: Result has more than 1000 rows. Consider filtering the query.")

    if not checks:
        checks.append("Result quality check passed.")

    return checks