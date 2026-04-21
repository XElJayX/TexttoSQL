# evaluation/golden_set.py
from app.llm.sql_generator import generate_sql
GOLDEN_SET = [

    # =========================
    # SIMPLE (single table)
    # =========================

    {
        "question": "how many companies are there?",
        "sql": "SELECT COUNT(*) FROM companies;",
        "complexity": "simple"
    },
    {
        "question": "how many users have never logged in?",
        "sql": "SELECT COUNT(*) FROM users WHERE last_login_at IS NULL;",
        "complexity": "simple"
    },
    {
        "question": "list all companies in the united states",
        "sql": "SELECT name FROM companies WHERE country = 'United States';",
        "complexity": "simple"
    },
    {
        "question": "how many active subscriptions are there?",
        "sql": "SELECT COUNT(*) FROM subscriptions WHERE status = 'active';",
        "complexity": "simple"
    },
    {
        "question": "what is the average invoice amount?",
        "sql": "SELECT AVG(amount_usd) FROM invoices;",
        "complexity": "simple"
    },


    # =========================
    # MEDIUM (2 table joins)
    # =========================

    {
        "question": "which companies have cancelled their subscriptions?",
        "sql": """SELECT c.name
                  FROM companies c
                  JOIN subscriptions s ON s.company_id = c.id
                  WHERE s.status = 'cancelled';""",
        "complexity": "medium"
    },
    {
        "question": "list users and their company names",
        "sql": """SELECT u.email, c.name
                  FROM users u
                  JOIN companies c ON u.company_id = c.id;""",
        "complexity": "medium"
    },
    {
        "question": "which subscriptions have generated invoices over 100 dollars?",
        "sql": """SELECT s.id
                  FROM subscriptions s
                  JOIN invoices i ON i.subscription_id = s.id
                  WHERE i.amount_usd > 100;""",
        "complexity": "medium"
    },
    {
        "question": "which companies are on a free tier plan?",
        "sql": """SELECT DISTINCT c.name
                  FROM companies c
                  JOIN subscriptions s ON s.company_id = c.id
                  JOIN plans p ON s.plan_id = p.id
                  WHERE p.tier = 'free';""",
        "complexity": "medium"
    },
    {
        "question": "which users have used any feature?",
        "sql": """SELECT DISTINCT u.email
                  FROM users u
                  JOIN feature_usage f ON f.user_id = u.id;""",
        "complexity": "medium"
    },


    # =========================
    # HARD (3+ tables, aggregations)
    # =========================

    {
        "question": "what is the total revenue collected per plan?",
        "sql": """SELECT p.name, SUM(i.amount_usd) AS total_revenue
                  FROM plans p
                  JOIN subscriptions s ON s.plan_id = p.id
                  JOIN invoices i ON i.subscription_id = s.id
                  WHERE i.status = 'paid'
                  GROUP BY p.name;""",
        "complexity": "hard"
    },
    {
        "question": "how many users does each company have?",
        "sql": """SELECT c.name, COUNT(u.id) AS user_count
                  FROM companies c
                  LEFT JOIN users u ON u.company_id = c.id
                  GROUP BY c.name;""",
        "complexity": "hard"
    },
    {
        "question": "what is the total revenue per company?",
        "sql": """SELECT c.name, SUM(i.amount_usd) AS total_revenue
                  FROM companies c
                  JOIN subscriptions s ON s.company_id = c.id
                  JOIN invoices i ON i.subscription_id = s.id
                  WHERE i.status = 'paid'
                  GROUP BY c.name;""",
        "complexity": "hard"
    },
    {
        "question": "which companies have not paid any invoices?",
        "sql": """SELECT c.name
                  FROM companies c
                  LEFT JOIN subscriptions s ON s.company_id = c.id
                  LEFT JOIN invoices i ON i.subscription_id = s.id AND i.status = 'paid'
                  WHERE i.id IS NULL;""",
        "complexity": "hard"
    },
    {
        "question": "what is the average feature usage per user per day?",
        "sql": """SELECT u.id, AVG(f.usage_count) AS avg_usage
                  FROM users u
                  JOIN feature_usage f ON f.user_id = u.id
                  GROUP BY u.id;""",
        "complexity": "hard"
    },
    {
        "question": "how many subscriptions were started in the last 30 days?",
        "sql": """SELECT COUNT(*)
                  FROM subscriptions
                  WHERE started_at >= NOW() - INTERVAL '30 days';""",
        "complexity": "hard"
    },
    {
        "question": "which plans generate the highest average revenue per subscription?",
        "sql": """SELECT p.name, AVG(i.amount_usd) AS avg_revenue
                  FROM plans p
                  JOIN subscriptions s ON s.plan_id = p.id
                  JOIN invoices i ON i.subscription_id = s.id
                  WHERE i.status = 'paid'
                  GROUP BY p.name
                  ORDER BY avg_revenue DESC;""",
        "complexity": "hard"
    },
]
def normalize(results):
    if results is None:
        return None
    return sorted([str(row) for row in results])

def execute_sql(sql: str) -> list[tuple]:
    from app.db.connection import get_connection

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)

        # Handle queries that don't return rows (e.g., INSERT, UPDATE)
        if cur.description is None:
            results = []
        else:
            results = cur.fetchall()

    except Exception as e:
        print(f"Error executing SQL:\n{sql}\nError: {e}")
        results = []

    finally:
        cur.close()
        conn.close()

    return results


def run_evaluation() -> dict:
    total = 0
    passed = 0  # FIX: this was missing

    complexity_breakdown = {
        "simple": {"total": 0, "passed": 0},
        "medium": {"total": 0, "passed": 0},
        "hard": {"total": 0, "passed": 0},
    }

    failed = []

    for item in GOLDEN_SET:
        total += 1

        question = item["question"]
        expected_sql = item["sql"]
        complexity = item["complexity"]

        # Track totals per complexity
        if complexity in complexity_breakdown:
            complexity_breakdown[complexity]["total"] += 1

        try:
            generated_sql = generate_sql(question)
        except Exception as e:
            print(f"Error generating SQL for question: {question}")
            print(f"Error: {e}")
            continue

        expected_sql_results = execute_sql(expected_sql)
        generated_sql_results = execute_sql(generated_sql)

        # Normalize results (important if order doesn't matter)
        if normalize(expected_sql_results) == normalize(generated_sql_results):
            passed += 1
            if complexity in complexity_breakdown:
                complexity_breakdown[complexity]["passed"] += 1
        else:
            failed.append({
                "question": question,
                "expected_sql": expected_sql,
                "generated_sql": generated_sql,
                "expected_results": expected_sql_results,
                "generated_results": generated_sql_results,
                "complexity": complexity
            })

    return {
        "total": total,
        "passed": passed,
        "failed_count": len(failed),
        "accuracy": passed / total if total > 0 else 0,
        "complexity_breakdown": complexity_breakdown,
        "failed_cases": failed,
    }


def format_results(results: dict) -> str:
    total = results["total"]
    passed = results["passed"]
    failed = results["failed_count"]

    accuracy = (passed / total * 100) if total > 0 else 0

    lines = []
    lines.append(f"Total:    {total}")
    lines.append(f"Passed:   {passed}  ({accuracy:.0f}%)")
    lines.append(f"Failed:   {failed}")
    lines.append("")
    lines.append("By complexity:")

    for level in ["simple", "medium", "hard"]:
        comp = results["complexity_breakdown"][level]
        t = comp["total"]
        p = comp["passed"]
        acc = (p / t * 100) if t > 0 else 0
        lines.append(f"  {level:<7}: {p}/{t}  ({acc:.0f}%)")

    lines.append("")
    lines.append("Failed questions:")

    for case in results["failed_cases"]:
        q = case["question"]
        comp = case["complexity"]
        lines.append(f'  - "{q}" ({comp})')

    return "\n".join(lines)
    
if __name__ == "__main__":
    results = run_evaluation()
    print(format_results(results))