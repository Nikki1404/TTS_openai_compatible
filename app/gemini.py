from auth import get_current_user_optional

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
    """
    Upload + parse Excel + persist dashboard rows.
    Authentication is OPTIONAL.
    If user is not logged in, created_by = 'anonymous'.
    """

    # --- Optional user logic ---
    user_id = current_user.id if current_user else "anonymous"

    # Validate type
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="File must be Excel (.xlsx/.xls)")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        required_columns = [
            "Audio File Name", "Audio Length", "Model",
            "Ground_truth", "Transcription", "WER Score",
            "Inference time (in sec)"
        ]

        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise HTTPException(400, f"Missing required columns: {missing}")

        data = df.to_dict("records")
        processed = []

        for i, row in enumerate(data):
            processed_row = {
                "Audio File Name": str(row.get("Audio File Name", "")),
                "Audio Length": float(row.get("Audio Length", 0)),
                "Model": str(row.get("Model", "")),
                "Ground_truth": str(row.get("Ground_truth", "")),
                "Transcription": str(row.get("Transcription", "")),
                "WER Score": float(row.get("WER Score", 0)),
                "Inference time (in sec)": float(row.get("Inference time (in sec)", 0))
            }
            processed.append(processed_row)

        # --- Persist to DB ---
        persist_dashboard_entries(db, processed, user_id)

        return FileUploadResponse(
            data=processed,
            message=f"Successfully processed {len(processed)} rows from {file.filename}"
        )

    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")
    finally:
        await file.close()
