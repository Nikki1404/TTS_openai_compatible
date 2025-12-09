from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
from database import SessionLocal
from schemas import FileUploadResponse
from crud import persist_dashboard_entries
from auth import get_current_user_optional
from models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------
# 🔥 NEW: Column Mapping Rules
# ------------------------------------------------------------
COLUMN_MAP = {
    "Audio File Name": ["file name", "audio_name", "audio file", "name"],
    "Audio Length": ["duration", "audio length (sec)", "length"],
    "Model": ["asr_model", "model name"],
    "Ground_truth": ["ground truth", "actual text", "reference"],
    "Transcription": ["asr output", "prediction", "transcript"],
    "WER Score": ["wer", "word error rate"],
    "Inference time (in sec)": ["latency", "inference", "time"]
}

REQUIRED_COLUMNS = list(COLUMN_MAP.keys())


# ------------------------------------------------------------
# 🔥 Helper: Auto-map or create missing columns
# ------------------------------------------------------------
def normalize_columns(df: pd.DataFrame):
    df_cols_lower = {c.lower(): c for c in df.columns}

    for required in REQUIRED_COLUMNS:
        if required in df.columns:
            continue  # column exists

        # try to find a similar column
        found = False
        for alt in COLUMN_MAP[required]:
            if alt.lower() in df_cols_lower:
                df[required] = df[df_cols_lower[alt.lower()]]
                found = True
                break

        # if still not found → create empty column
        if not found:
            df[required] = ""

    return df


# ------------------------------------------------------------
# 🔥 Helper: Convert complex time formats → seconds
# ------------------------------------------------------------
def parse_time_value(value):
    if value is None or str(value).strip() in ["", "nan", "NaN"]:
        return 0.0

    s = str(value).strip()

    # Case 1: "1 day, 0:03:22"
    if "day" in s:
        parts = s.split(",")
        days = int(parts[0].split()[0])
        time_part = parts[1].strip()
        t = list(reversed(time_part.split(":")))
        seconds = sum(float(x) * (60 ** idx) for idx, x in enumerate(t))
        return days * 86400 + seconds

    # Case 2: "06:44:00" or "03:22"
    if ":" in s:
        t = list(reversed(s.split(":")))
        return sum(float(x) * (60 ** idx) for idx, x in enumerate(t))

    # Case 3: Plain numeric
    try:
        return float(s)
    except:
        raise ValueError(f"Invalid time format: {s}")


# ------------------------------------------------------------
# 📌 MAIN UPLOAD ENDPOINT
# ------------------------------------------------------------
@router.post(
    "/upload",
    response_model=FileUploadResponse,
    tags=["Benchmarks"]
)
async def upload_benchmark_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):

    user_id = current_user.id if current_user else "anonymous"

    # Validate file extension
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "File must be an Excel file (.xlsx or .xls)")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        # ------------------------------------------------------------
        # 🔥 STEP 1 — Clean whitespace + Drop blank rows
        # ------------------------------------------------------------
        df = df.replace(r'^\s*$', pd.NA, regex=True)
        df = df.dropna(how="all")

        if df.empty:
            raise HTTPException(400, "The uploaded file contains no usable data.")

        # ------------------------------------------------------------
        # 🔥 STEP 2 — Auto-map or create missing required columns
        # ------------------------------------------------------------
        df = normalize_columns(df)

        # Now df ALWAYS has all required columns.

        # ------------------------------------------------------------
        # 🔥 STEP 3 — Convert rows to dict & clean values
        # ------------------------------------------------------------
        processed_data = []

        for i, row in df.iterrows():

            try:
                audio_length = parse_time_value(row["Audio Length"])
                inference_time = parse_time_value(row["Inference time (in sec)"])

                # WER
                wer_raw = row["WER Score"]
                if pd.isna(wer_raw) or str(wer_raw).strip() == "":
                    wer_score = 0.0
                else:
                    wer_score = float(wer_raw)

                processed_row = {
                    "Audio File Name": str(row["Audio File Name"]),
                    "Audio Length": audio_length,
                    "Model": str(row["Model"]),
                    "Ground_truth": str(row["Ground_truth"]),
                    "Transcription": str(row["Transcription"]),
                    "WER Score": wer_score,
                    "Inference time (in sec)": inference_time
                }

                processed_data.append(processed_row)

            except Exception as e:
                raise HTTPException(
                    400,
                    f"Invalid data in row {i+2}: {str(e)}"
                )

        # ------------------------------------------------------------
        # 🔥 STEP 4 — Insert into DB
        # ------------------------------------------------------------
        persist_dashboard_entries(db, processed_data, user_id)

        return FileUploadResponse(
            data=processed_data,
            message=f"Successfully processed {len(processed_data)} rows from {file.filename}"
        )

    except Exception as e:
        raise HTTPException(500, f"An error occurred while processing the file: {e}")

    finally:
        await file.close()
