import os

SQLALCHEMY_TRACK_MODIFICATIONS = False
PGUSER = os.environ.get("PGUSER", "user")
PGPASSWORD = os.environ.get("PGPASSWORD", "pass")
PGDATABASE = os.environ.get("PGDATABASE", "hp")

DATABASE_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@localhost:5432/{PGDATABASE}"
SQLALCHEMY_DATABASE_URI = DATABASE_URL
CELERY_BROKER_URL = "sqla+" + DATABASE_URL
CELERY_RESULT_BACKEND = "db+" + DATABASE_URL
