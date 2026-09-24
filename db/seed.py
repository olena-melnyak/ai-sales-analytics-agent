import os
import random
from datetime import datetime, timedelta, timezone

import psycopg
from dotenv import load_dotenv
from faker import Faker


load_dotenv()

fake = Faker()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


CHANNELS = [
    "Google Ads",
    "LinkedIn",
    "Facebook",
    "Email",
    "Referral",
    "Organic Search",
]

STATUSES = [
    "new",
    "contacted",
    "qualified",
    "proposal",
    "won",
    "lost",
]

ACTIVITY_TYPES = [
    "call",
    "email",
    "meeting",
    "message",
]

MANAGERS = [
    "Anna",
    "Oleh",
    "Maria",
    "Dmytro",
    "Iryna",
]

INDUSTRIES = [
    "Technology",
    "Finance",
    "Healthcare",
    "Retail",
    "Manufacturing",
    "Education",
]

COMPANY_SIZES = [
    "1-10",
    "11-50",
    "51-200",
    "201-500",
    "500+",
]


def random_date(days_back: int = 365) -> datetime:
    """Generate a random datetime within the last year."""
    return datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def get_connection():
    """Create a PostgreSQL connection."""
    return psycopg.connect(**DB_CONFIG)


def clear_data(conn):
    """Remove previously generated data."""
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                audit_log,
                sales,
                activities,
                leads,
                campaigns,
                customers
            RESTART IDENTITY CASCADE;
            """
        )


def seed_campaigns(conn):
    """Create marketing campaigns."""
    campaigns = [
        ("Google Search Q1", "Google Ads", 5000),
        ("Google Search Q2", "Google Ads", 6000),
        ("LinkedIn B2B Q1", "LinkedIn", 8000),
        ("LinkedIn IT Decision Makers", "LinkedIn", 7000),
        ("Facebook SMB Campaign", "Facebook", 3000),
        ("Email Outreach Q1", "Email", 2000),
        ("Email Outreach Q2", "Email", 2500),
        ("Partner Program", "Referral", 3000),
        ("SEO Content", "Organic Search", 1000),
        ("Retargeting Campaign", "Google Ads", 4000),
    ]

    campaign_ids = []

    with conn.cursor() as cur:
        for name, channel, budget in campaigns:
            cur.execute(
                """
                INSERT INTO campaigns
                    (campaign_name, channel, budget, start_date, end_date)
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING campaign_id;
                """,
                (
                    name,
                    channel,
                    budget,
                    datetime.now(timezone.utc).date() - timedelta(days=365),
                    datetime.now(timezone.utc).date(),
                ),
            )

            campaign_ids.append(cur.fetchone()[0])

    return campaign_ids


def seed_customers(conn, count=100):
    """Create customer companies."""
    customer_ids = []

    with conn.cursor() as cur:
        for _ in range(count):
            cur.execute(
                """
                INSERT INTO customers
                    (company_name, industry, country, company_size, 
created_at)
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING customer_id;
                """,
                (
                    fake.company(),
                    random.choice(INDUSTRIES),
                    fake.country(),
                    random.choice(COMPANY_SIZES),
                    random_date(),
                ),
            )

            customer_ids.append(cur.fetchone()[0])

    return customer_ids


def seed_leads(conn, customer_ids, campaign_ids, count=500):
    """Create leads using a realistic sales funnel."""
    lead_data = []

    with conn.cursor() as cur:
        for _ in range(count):
            campaign_id = random.choice(campaign_ids)

            cur.execute(
                """
                SELECT channel
                FROM campaigns
                WHERE campaign_id = %s;
                """,
                (campaign_id,),
            )

            channel = cur.fetchone()[0]

            # Simulate the lead moving through the sales funnel.
            status = "new"

            if random.random() < 0.75:
                status = "contacted"

                if random.random() < 0.65:
                    status = "qualified"

                    if random.random() < 0.60:
                        status = "proposal"

                        if random.random() < 0.55:
                            status = "won"

            # Some leads are lost before reaching "won".
            if status != "won" and random.random() < 0.20:
                status = "lost"

            customer_id = (
                random.choice(customer_ids)
                if status in {"qualified", "proposal", "won", "lost"}
                else None
            )

            estimated_value = round(
                random.uniform(500, 15000),
                2,
            )

            created_at = random_date()

            cur.execute(
                """
                INSERT INTO leads
                    (
                        customer_id,
                        campaign_id,
                        source,
                        status,
                        estimated_value,
                        created_at,
                        assigned_manager
                    )
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                RETURNING lead_id;
                """,
                (
                    customer_id,
                    campaign_id,
                    channel,
                    status,
                    estimated_value,
                    created_at,
                    random.choice(MANAGERS),
                ),
            )

            lead_id = cur.fetchone()[0]

            lead_data.append(
                {
                    "lead_id": lead_id,
                    "status": status,
                    "created_at": created_at,
                }
            )

    return lead_data

def seed_activities(conn, lead_data):
    """Create activities for a subset of leads."""
    with conn.cursor() as cur:
        for lead in lead_data:
            # Some leads intentionally have no activity.
            if random.random() < 0.15:
                continue
            activity_ranges = {
                "new": (0, 1),
                "contacted": (1, 2),
                "qualified": (2, 4),
                "proposal": (3, 5),
                "won": (4, 6),
                "lost": (1, 4),
            }

            activity_count = random.randint(*activity_ranges[lead["status"]])
            for _ in range(activity_count):
                activity_date = min(
                      lead["created_at"] +timedelta(hours=random.randint(1, 240)),
                      datetime.now(timezone.utc),                
            )

                cur.execute(
                    """
                    INSERT INTO activities
                        (
                            lead_id,
                            activity_type,
                            activity_date,
                            manager_id,
                            notes
                        )
                    VALUES
                        (%s, %s, %s, %s, %s);
                    """,
                    (
                        lead["lead_id"],
                        random.choice(ACTIVITY_TYPES),
                        activity_date,
                        random.choice(MANAGERS),
                        fake.sentence(),
                    ),
                )


def seed_sales(conn, lead_data):
    """Create sales for won leads."""
    sales_count = 0

    with conn.cursor() as cur:
        for lead in lead_data:
            if lead["status"] != "won":
                continue

            amount = round(random.uniform(1000, 25000), 2)

            sale_date = min(
                lead["created_at"] + timedelta(days=random.randint(5, 90)),
                datetime.now(timezone.utc),
            )
            cur.execute(
                """
                INSERT INTO sales
                    (
                        lead_id,
                        amount,
                        sale_date,
                        status
                    )
                VALUES
                    (%s, %s, %s, %s);
                """,
                (
                    lead["lead_id"],
                    amount,
                    sale_date,
                    "completed",
                ),
            )

            sales_count += 1

    return sales_count


def main():
    print("Starting database seeding...")

    with get_connection() as conn:
        clear_data(conn)

        print("Creating campaigns...")
        campaign_ids = seed_campaigns(conn)

        print("Creating customers...")
        customer_ids = seed_customers(conn)

        print("Creating leads...")
        lead_data = seed_leads(
            conn,
            customer_ids,
            campaign_ids,
        )

        print("Creating activities...")
        seed_activities(conn, lead_data)

        print("Creating sales...")
        sales_count = seed_sales(conn, lead_data)

        conn.commit()

    print("Database seeding completed successfully.")
    print(f"Customers: {len(customer_ids)}")
    print(f"Campaigns: {len(campaign_ids)}")
    print(f"Leads: {len(lead_data)}")
    print(f"Sales: {sales_count}")


if __name__ == "__main__":
    main()
