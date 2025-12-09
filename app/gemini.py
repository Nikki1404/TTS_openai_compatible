from fastapi import Depends
from auth import get_current_user_optional
from crud import persist_dashboard_entries
from database import SessionLocal

@router.post(
    "/upload", 
    response_model=FileUploadResponse,
    summary="Upload benchmark Excel file",
    description="Upload and process an Excel file containing ASR benchmark data",
    response_description="Processed benchmark data ready for analysis",
    responses={
        200: {"description": "File processed successfully"},
        400: {"description": "Invalid file format or missing required columns"},
        500: {"description": "Server error during file processing"}
    },
    tags=["Benchmarks"]
)
async def upload_benchmark_file(
    file: UploadFile = File(
        ..., 
        description="Excel file (.xlsx or .xls) containing benchmark data",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Upload and process an Excel file containing ASR benchmark data.
    Authentication is OPTIONAL.
    If user is not logged in → created_by = 'anonymous'
    """
    
    # Determine created_by user
    user_id = current_user.id if current_user else "anonymous"

    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
    
    try:
        # Read file
        contents = await file.read()
        
        # Parse Excel
        df = pd.read_excel(io.BytesIO(contents))
        
        # Required columns
        required_columns = [
            'Audio File Name', 'Audio Length', 'Model', 
            'Ground_truth', 'Transcription', 'WER Score', 
            'Inference time (in sec)'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        data = df.to_dict('records')
        
        # Clean rows
        processed_data = []
        for i, row in enumerate(data):
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
            except (ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid data in row {i+2}: {str(e)}"
                )
        
        if not processed_data:
            raise HTTPException(status_code=400, detail="No valid data found in the file")

        # ⭐ NEW: Persist into Dashboard DB (existing feature preserved)
        persist_dashboard_entries(db, processed_data, user_id)

        # ⭐ Original return preserved
        return FileUploadResponse(
            data=processed_data,
            message=f"Successfully processed {len(processed_data)} rows from {file.filename}"
        )

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse the Excel file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {str(e)}")
    finally:
        await file.close()
