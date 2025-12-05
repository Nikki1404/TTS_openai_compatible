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
