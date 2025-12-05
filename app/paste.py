from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
from typing import List

from database import SessionLocal
from schemas import FileUploadResponse
from crud import persist_dashboard_entries
from auth import get_current_active_user
from models import User


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    summary="Upload benchmark Excel file",
    description="Upload and process an Excel file containing ASR benchmark data",
    tags=["Benchmarks"]
)
async def upload_benchmark_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        required_columns = [
            'Audio File Name', 'Audio Length', 'Model', 
            'Ground_truth', 'Transcription', 'WER Score', 
            'Inference time (in sec)'
        ]
        
        missing_columns = [c for c in required_columns if c not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        raw_rows = df.to_dict('records')

        processed_data = []
        for i, row in enumerate(raw_rows):
            try:
                processed_row = {
                    'Audio File Name': str(row.get('Audio File Name', '')),
                    'Audio Length': float(row.get('Audio Length', 0)),
                    'Model': str(row.get('Model', '')),
                    'Ground_truth': str(row.get('Ground_truth', '')),
                    'Transcription': str(row.get('Transcription', '')),
                    'WER Score': float(row.get('WER Score', 0)),
                    'Inference time (in sec)': float(row.get('Inference time (in sec)', 0))
                }
                processed_data.append(processed_row)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid data in row {i+2}: {str(e)}"
                )

        if not processed_data:
            raise HTTPException(status_code=400, detail="No valid data found.")

        saved_entries = persist_dashboard_entries(
            db=db,
            rows=processed_data,
            user_id=current_user.id
        )

        return FileUploadResponse(
            data=processed_data,
            message=f"Successfully processed & saved {len(saved_entries)} rows from {file.filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

    finally:
        await file.close()



def persist_dashboard_entries(
    db: Session,
    rows: Union[Dict, List[Dict]],
    user_id: str
):
    """
    Universal persistence function:
    - Accepts one dict OR list of dicts.
    - Auto-detects single vs multiple entries.
    - Uses bulk insert for performance.
    - Safe for concurrent writes.
    - Automatically rolls back on error.
    """

    # Normalize input → always list
    if isinstance(rows, dict):
        rows = [rows]

    entries = []

    try:
        for r in rows:
            entry = DashboardData(
                id=str(uuid.uuid4()),
                audio_file_name=r.get("Audio File Name"),
                audio_length=r.get("Audio Length"),
                model=r.get("Model"),
                ground_truth=r.get("Ground_truth"),
                transcription=r.get("Transcription"),
                wer_score=r.get("WER Score"),
                inference_time=r.get("Inference time (in sec)"),
                created_by=user_id
            )
            entries.append(entry)

        if len(entries) == 1:
            db.add(entries[0])
            db.commit()
            db.refresh(entries[0])
        else:
            db.bulk_save_objects(entries)
            db.commit()

        return entries

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to persist dashboard entries: {e}")

