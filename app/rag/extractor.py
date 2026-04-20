#Interesting file, Introspects the DB and builds a rich text description of each table
from app.db.connection import get_connection

def extract_schema():
    conn = get_connection()
    cur = conn.cursor()

    #GET ALL TABLES IN THE PUBLIC SCHEMA
    cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema='public' AND table_type='BASE TABLE'
    ORDER BY table_name
    """)

    tables = [row[0] for row in cur.fetchall()]

    schema_chunks = []

    for table in tables:
        # GET COLUMNS WITH TYPES AND NULLABLE INFO
        cur.execute("""
        SELECT column_name,data_type,is_nullable
        FROM information_schema.columns
        WHERE table_name=%s AND table_schema='public'
        ORDER BY ordinal_position
        """,(table,))

        columns=cur.fetchall()

        #get foreign keys
        cur.execute("""
        SELECT kcu.column_name, ccu.table_name AS foreign_table
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
        on ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name=%s
        """,(table,))

        foreign_keys = cur.fetchall()

        #get 3 sample row to help LLM understand

        cur.execute(f"SELECT * FROM {table} LIMIT 3")
        sample_rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]

        TABLE_DESCRIPTIONS = {
        "companies": (
            "Represents customer organizations (B2B accounts). Each company is the top-level entity "
            "that owns users and subscriptions. Use this table for questions about organizations, "
            "customer segmentation (industry, country), account creation trends, or identifying which "
            "companies performed certain actions. Join with users (company_id), subscriptions (company_id), "
            "and plans (via subscriptions) to analyze customer behavior, revenue, or lifecycle. "
            "Key fields: industry, country, created_at."
        ),

        "users": (
            "Represents individual user accounts belonging to companies. Each user is linked to a company "
            "via company_id. Use for analyzing user activity, engagement, and login behavior. "
            "Useful for queries like active vs inactive users, last login trends, or role-based analysis. "
            "Join with feature_usage (user_id) for engagement analytics and subscriptions (indirectly via company) "
            "to understand how user behavior relates to billing. "
            "Key fields: email, role, created_at, last_login_at, never logged in, inactive"
        ),

        "plans": (
            "Defines available subscription plans and pricing tiers. Each plan includes pricing and feature limits. "
            "Use this table for pricing analysis, tier comparisons, and feature availability (e.g., analytics, API access). "
            "Join with subscriptions (plan_id) to understand which companies are on which plans and how pricing impacts revenue. "
            "Key fields: tier, monthly_price_usd, max_seats, has_analytics, has_api_access."
        ),

        "subscriptions": (
            "Represents active and historical subscriptions for companies. Each subscription links a company to a plan. "
            "Use for lifecycle analysis such as active subscriptions, churn (cancelled_at), upgrades/downgrades, "
            "and seat usage. This is the central table for revenue-related joins. "
            "Join with invoices (subscription_id) for billing data and subscription_events for lifecycle changes. "
            "Key fields: status (active, cancelled, trialing, etc.), started_at, cancelled_at, seat_count."
        ),

        "invoices": (
            "Primary table for revenue and financial analysis. Use for MRR, ARR, "
            "total revenue, monthly recurring revenue, payment collection rates, "
            "unpaid invoices, outstanding balances, overdue payments, and billing timelines. "
            "Each invoice is a payment attempt for a subscription with an amount and status. "
            "Key fields: amount_usd, status (paid, failed, pending, refunded), issued_at, paid_at."
        ),

        "subscription_events": (
            "Event log capturing all changes and lifecycle actions for subscriptions. Each row represents an event such as "
            "trial_started, upgraded, downgraded, cancelled, or payment_failed. Use this table for temporal and behavioral "
            "analysis of subscription changes over time. Ideal for answering questions about when events occurred, "
            "conversion funnels (trial → paid), upgrade/downgrade patterns, and churn signals. "
            "Join with subscriptions (subscription_id) and optionally companies for customer-level insights. "
            "Key fields: event_type, metadata (JSON with additional context), occurred_at."
        ),

        "feature_usage": (
            "Tracks daily usage of product features at the user level. Each record represents "
            "how many times a user used a specific feature on a given date. Use for product analytics, "
            "engagement metrics, feature adoption, and cohort analysis. "
            "Key fields: feature_name, usage_count, usage_date."
        ),
    }

        #BUILD human readable text description of the table
        chunk = f"Table: {table}\n"
        if table in TABLE_DESCRIPTIONS:
            chunk += f"Description: {TABLE_DESCRIPTIONS[table]}\n"
        chunk += "Columns:\n"
        for col_name, data_type, nullable in columns:
            null_str = "nullable" if nullable=="YES" else "not nullable"
            chunk += f"  - {col_name} ({data_type}, {null_str})\n"
        
        if foreign_keys:
            chunk += "Relationships:\n"
            for col, ref_table in foreign_keys:
                chunk += f"  - {col} references {ref_table}.id\n"
        
        if sample_rows:
            chunk += "Sample data:\n"
            for row in sample_rows:
                row_dict = dict(zip(col_names, row))
                # Truncate long values so chunks stay compact
                row_str = {k: str(v) for k, v in row_dict.items() if v is not None}
                chunk += f"  {row_str}\n"
        schema_chunks.append({
            "table_name": table,
            "chunk": chunk
        })

    cur.close()
    conn.close()
    return schema_chunks


if __name__ == "__main__":
    chunks = extract_schema()
    for c in chunks:
        print(f"\n{'='*50}")
        print(c["chunk"])
