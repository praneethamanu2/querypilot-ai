def recommend_chart_type(intent: str, columns: list = None) -> str:
    """
    Recommends a chart type based on question intent and result columns.

    For rule-based queries, intent is usually enough.
    For LLM-generated queries, columns help decide the chart.
    """

    if columns is None:
        columns = []

    if intent in [
        "revenue_by_region",
        "revenue_by_category",
        "top_customers",
        "return_rate_by_category",
        "average_order_value_by_region",
        "discount_analysis"
    ]:
        return "bar"

    if intent == "monthly_revenue_trend":
        return "line"

    # Fallback logic for LLM-generated queries
    if len(columns) >= 2:
        first_column = columns[0].lower()

        if "month" in first_column or "date" in first_column:
            return "line"

        return "bar"

    return "table"