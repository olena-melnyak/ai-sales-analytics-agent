import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "sales_analytics"),
    "user": os.getenv("DB_USER", "analytics_user"),
    "password": os.getenv("DB_PASSWORD", "analytics_password"),
}


def get_connection():
    """Create a connection to the PostgreSQL database."""
    return psycopg.connect(**DB_CONFIG)
