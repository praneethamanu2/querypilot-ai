def recommend_chart_type(intent: str) -> str:
    """
    Recommends a chart type based on the question intent.
    """

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

    return "table"