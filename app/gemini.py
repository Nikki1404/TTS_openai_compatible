wer_raw = row.get("WER Score", 0)
            if wer_raw is None or str(wer_raw).strip() == "" or pd.isna(wer_raw):
                wer_score = 0.0
            else:
                try:
                    wer_score = float(wer_raw)
                except:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid WER Score in row {i+2}: {wer_raw}"
                    )
