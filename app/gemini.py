curl -X 'POST' \
  'http://127.0.0.1:8000/api/benchmarks/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@asr_benchmarking_Q2_2025 (1).xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

	
                audio_length_raw = str(row.get("Audio Length", "")).strip()
                
                if audio_length_raw == "" or audio_length_raw.lower() == "nan":
                    audio_length = 0.0

                elif "day" in audio_length_raw:
                    # e.g., "1 day, 0:03:22"
                    day_part, time_part = audio_length_raw.split(",")
                    days = int(day_part.split()[0])
                    parts = list(reversed(time_part.strip().split(":")))
                    seconds = sum(float(x) * (60 ** idx) for idx, x in enumerate(parts))
                    audio_length = days * 86400 + seconds

                elif ":" in audio_length_raw:
                    # e.g., "06:44:00"
                    parts = list(reversed(audio_length_raw.split(":")))
                    audio_length = sum(float(x) * (60 ** idx) for idx, x in enumerate(parts))

                else:
                    audio_length = float(audio_length_raw)

                # -------------------------------
                # FIX 2: Convert "Inference time"
                # -------------------------------
                inf_raw = str(row.get("Inference time (in sec)", "")).strip()
                
                if inf_raw == "" or inf_raw.lower() == "nan":
                    inference_time = 0.0

                elif "day" in inf_raw:
                    day_part, time_part = inf_raw.split(",")
                    days = int(day_part.split()[0])
                    parts = list(reversed(time_part.strip().split(":")))
                    seconds = sum(float(x) * (60 ** idx) for idx, x in enumerate(parts))
                    inference_time = days * 86400 + seconds

                elif ":" in inf_raw:
                    parts = list(reversed(inf_raw.split(":")))
                    inference_time = sum(float(x) * (60 ** idx) for idx, x in enumerate(parts))

                else:
                    inference_time = float(inf_raw)
