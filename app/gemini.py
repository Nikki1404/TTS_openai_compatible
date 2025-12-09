# test_db.py

import os
from database import SessionLocal
from models import DashboardData  # adjust name if needed
from sqlalchemy import inspect

# ---------------------------------------------------------
# 1. Show absolute path of the database file
# ---------------------------------------------------------
db_file = "asr_benchmark.db"
print("==================================================")
print("📌 SQLite Database File Check")
print("Absolute DB Path:", os.path.abspath(db_file))
print("Exists:", os.path.exists(db_file))
print("==================================================\n")

# ---------------------------------------------------------
# 2. Create DB session
# ---------------------------------------------------------
db = SessionLocal()

# ---------------------------------------------------------
# 3. Verify the table exists in the SQLite schema
# ---------------------------------------------------------
print("📌 Checking if 'dashboard_data' table exists...")

inspector = inspect(db.bind)
tables = inspector.get_table_names()
print("Tables found in DB:", tables)

if "dashboard_data" not in tables:
    print("❌ ERROR: 'dashboard_data' table NOT found in database.")
    print("Make sure your models & Base.metadata.create_all() have run.")
    exit(1)

print("✅ Table exists!\n")

# ---------------------------------------------------------
# 4. Fetch all rows from dashboard_data
# ---------------------------------------------------------
print("📌 Fetching rows from dashboard_data...\n")

rows = db.query(DashboardData).all()
print(f"Total rows in dashboard_data: {len(rows)}\n")

# ---------------------------------------------------------
# 5. Show first 5 rows (to avoid huge output)
# ---------------------------------------------------------
for r in rows[:5]:
    print({
        "id": r.id,
        "audio_file_name": r.audio_file_name,
        "audio_length": r.audio_length,
        "model": r.model,
        "wer_score": r.wer_score,
        "inference_time": r.inference_time,
        "created_by": r.created_by,
    })
    print("--------------------------------------------------")

db.close()
print("\n✅ Done.")
