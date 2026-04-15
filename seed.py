import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from app.db.connection import get_connection
from psycopg2.extras import execute_values, register_uuid
import uuid

fake = Faker()
register_uuid()

conn = get_connection()


cur = conn.cursor()

INDUSTRIES = ['Finance', 'Healthcare', 'Retail', 'Education',
              'Logistics', 'Legal', 'Marketing', 'Engineering']

COUNTRIES = ['US', 'UK', 'Canada', 'Germany', 'Australia', 'France']


def seed_companies(n=200):
    companies = [
        (
            uuid.uuid4(),
            fake.company(),
            random.choice(INDUSTRIES),
            random.choice(COUNTRIES),
            fake.date_time_between(start_date='-5y', end_date='now')
        )
        for _ in range(n)
    ]

    execute_values(cur, """
        INSERT INTO companies (id, name, industry, country, created_at)
        VALUES %s
    """, companies)

    print(f"Inserted {n} companies")
    return [c[0] for c in companies]


def seed_plans():
    plans = [
        (uuid.uuid4(), 'Free', 'free', 0.00, 3, False, False),
        (uuid.uuid4(), 'Student', 'student', 29.00, 10, True, False),
        (uuid.uuid4(), 'Pro', 'pro', 99.00, 50, True, True),
        (uuid.uuid4(), 'Enterprise', 'enterprise', 499.00, 500, True, True),
    ]

    execute_values(cur, """
        INSERT INTO plans 
        (id, name, tier, monthly_price_usd, max_seats, has_analytics, has_api_access)
        VALUES %s
    """, plans)

    print("Seeded 4 plans")
    return [p[0] for p in plans]


ROLES = ['admin', 'member', 'viewer']


def seed_users(company_ids, n=1000):
    users = []

    for _ in range(n):
        created = fake.date_time_between(start_date='-2y', end_date='-1m')

        last_login = (
            None if random.random() < 0.15
            else fake.date_time_between(start_date=created, end_date='now')
        )

        users.append((
            uuid.uuid4(),
            random.choice(company_ids),
            fake.unique.email(),
            random.choice(ROLES),
            created,
            last_login
        ))

    execute_values(cur, """
        INSERT INTO users 
        (id, company_id, email, role, created_at, last_login_at)
        VALUES %s
    """, users)

    print(f"Seeded {n} users")
    return [u[0] for u in users]


STATUSES = ['active', 'cancelled', 'paused', 'trialing']


def seed_subscriptions(company_ids, plan_ids):
    subscriptions = []

    for company_id in company_ids:
        started = fake.date_time_between(start_date='-2y', end_date='-3m')

        status = random.choices(
            STATUSES, weights=[60, 25, 10, 5]
        )[0]

        cancelled_at = (
            fake.date_time_between(start_date=started, end_date='now')
            if status == 'cancelled' else None
        )

        subscriptions.append((
            uuid.uuid4(),
            company_id,
            random.choice(plan_ids),
            status,
            started,
            cancelled_at,
            random.randint(1, 50)
        ))

    execute_values(cur, """
        INSERT INTO subscriptions
        (id, company_id, plan_id, status, started_at, cancelled_at, seat_count)
        VALUES %s
    """, subscriptions)

    print(f"Seeded {len(subscriptions)} subscriptions")
    return [s[0] for s in subscriptions], subscriptions


def seed_invoices(subscriptions_data):
    invoices = []

    for sub_id, _, _, _, started_at, cancelled_at, _ in subscriptions_data:
        end = cancelled_at or datetime.now()

        current = started_at
        while current < end:
            is_paid = random.random() > 0.08

            invoices.append((
                uuid.uuid4(),
                sub_id,
                random.choice([29.00, 99.00, 499.00]),
                'paid' if is_paid else 'failed',
                current,
                current + timedelta(days=random.randint(1, 5)) if is_paid else None
            ))

            current += timedelta(days=30)

    execute_values(cur, """
        INSERT INTO invoices
        (id, subscription_id, amount_usd, status, issued_at, paid_at)
        VALUES %s
    """, invoices)

    print(f"Seeded {len(invoices)} invoices")


def seed_events(subscription_ids):
    event_types = [
        'plan_upgraded', 'plan_downgraded', 'seat_added',
        'seat_removed', 'payment_failed', 'trial_started', 'trial_converted'
    ]

    events = []

    for sub_id in subscription_ids:
        for _ in range(random.randint(1, 8)):
            events.append((
                uuid.uuid4(),
                sub_id,
                random.choice(event_types),
                '{}',
                fake.date_time_between(start_date='-2y', end_date='now')
            ))

    execute_values(cur, """
        INSERT INTO subscription_events
        (id, subscription_id, event_type, metadata, occurred_at)
        VALUES %s
    """, events)

    print(f"Seeded {len(events)} events")


def seed_feature_usage(user_ids):
    features = ['dashboard', 'reports', 'api', 'exports',
                'integrations', 'team_mgmt', 'billing']

    usage = []

    for user_id in random.sample(user_ids, min(800, len(user_ids))):
        for _ in range(random.randint(5, 30)):
            usage.append((
                uuid.uuid4(),
                user_id,
                random.choice(features),
                random.randint(1, 100),
                fake.date_between(start_date='-1y', end_date='today')
            ))

    execute_values(cur, """
        INSERT INTO feature_usage
        (id, user_id, feature_name, usage_count, usage_date)
        VALUES %s
    """, usage)

    print(f"Seeded {len(usage)} feature usage rows")


if __name__ == "__main__":
    print("Seeding database...")

    company_ids = seed_companies(200)
    plan_ids = seed_plans()
    user_ids = seed_users(company_ids, 1000)
    sub_ids, sub_data = seed_subscriptions(company_ids, plan_ids)

    seed_invoices(sub_data)
    seed_events(sub_ids)
    seed_feature_usage(user_ids)

    conn.commit()
    cur.close()
    conn.close()

    print("Done!")