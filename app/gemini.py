from database import SessionLocal
from models import DashboardData  # your model name, adjust if different

db = SessionLocal()

rows = db.query(DashboardData).all()

print(f"Total rows in dashboard_data: {len(rows)}")

for r in rows[:5]:  # print only first 5 rows
    print({
        "id": r.id,
        "audio_file_name": r.audio_file_name,
        "audio_length": r.audio_length,
        "model": r.model,
        "wer_score": r.wer_score,
        "inference_time": r.inference_time,
        "created_by": r.created_by
    })
