def generate_sql_from_question(question: str) -> dict:
    """
    Converts a natural language business question into a SQL query.

    This is a rule-based MVP.
    It checks keywords in the question and returns a matching SQL query.
    """

    question_lower = question.lower()

    if "revenue by region" in question_lower or "sales by region" in question_lower:
        sql = """
        SELECT 
            c.region,
            ROUND(SUM(o.revenue), 2) AS total_revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY total_revenue DESC
        """
        intent = "revenue_by_region"

    elif "revenue by category" in question_lower or "sales by category" in question_lower:
        sql = """
        SELECT 
            p.category,
            ROUND(SUM(o.revenue), 2) AS total_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.category
        ORDER BY total_revenue DESC
        """
        intent = "revenue_by_category"

    elif "monthly sales" in question_lower or "monthly revenue" in question_lower or "sales trend" in question_lower:
        sql = """
        SELECT 
            SUBSTR(o.order_date, 1, 7) AS month,
            ROUND(SUM(o.revenue), 2) AS total_revenue
        FROM orders o
        GROUP BY month
        ORDER BY month
        """
        intent = "monthly_revenue_trend"

    elif "top customers" in question_lower or "top 10 customers" in question_lower:
        sql = """
        SELECT 
            c.customer_name,
            c.region,
            ROUND(SUM(o.revenue), 2) AS total_revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.customer_name, c.region
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        intent = "top_customers"

    elif "return rate" in question_lower or "returns by category" in question_lower:
        sql = """
        SELECT
            p.category,
            COUNT(*) AS total_orders,
            SUM(o.returned) AS returned_orders,
            ROUND(100.0 * SUM(o.returned) / COUNT(*), 2) AS return_rate_percent
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.category
        ORDER BY return_rate_percent DESC
        """
        intent = "return_rate_by_category"

    elif "average order value" in question_lower or "aov" in question_lower:
        sql = """
        SELECT
            c.region,
            ROUND(AVG(o.revenue), 2) AS average_order_value
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY average_order_value DESC
        """
        intent = "average_order_value_by_region"

    elif "discount" in question_lower:
        sql = """
        SELECT
            c.region,
            ROUND(AVG(o.discount) * 100, 2) AS average_discount_percent,
            ROUND(SUM(o.revenue), 2) AS total_revenue
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.region
        ORDER BY average_discount_percent DESC
        """
        intent = "discount_analysis"

    else:
        sql = """
        SELECT 
            COUNT(*) AS total_orders,
            ROUND(SUM(revenue), 2) AS total_revenue,
            ROUND(AVG(revenue), 2) AS average_order_value
        FROM orders
        """
        intent = "general_summary"

    return {
        "intent": intent,
        "sql_query": sql.strip()
    }


def explain_generated_sql(intent: str) -> str:
    """
    Explains what the generated SQL is doing in plain English.
    """

    explanations = {
        "revenue_by_region": "This query calculates total revenue for each customer region and ranks regions from highest to lowest revenue.",
        "revenue_by_category": "This query calculates total revenue for each product category and ranks categories by sales performance.",
        "monthly_revenue_trend": "This query groups orders by month and calculates total monthly revenue to show sales trends over time.",
        "top_customers": "This query identifies the top customers by total revenue.",
        "return_rate_by_category": "This query calculates the percentage of returned orders for each product category.",
        "average_order_value_by_region": "This query calculates the average order value for each region.",
        "discount_analysis": "This query compares average discount levels and total revenue by region.",
        "general_summary": "This query gives an overall business summary including total orders, total revenue, and average order value."
    }

    return explanations.get(intent, "This query answers the business question using the available database tables.")