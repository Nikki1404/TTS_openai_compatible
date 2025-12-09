curl -X 'POST' \
  'http://127.0.0.1:8000/api/benchmarks/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@asr_benchmarking_Q2_2025 (1).xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

	
                audio_length_raw = str(row.get('Audio Length', '')).strip()
                if audio_length_raw.replace('.', '', 1).isdigit():
                    audio_length = float(audio_length_raw)
                elif ":" in audio_length_raw:
                    # Convert HH:MM:SS → seconds
                    parts = list(reversed(audio_length_raw.split(":")))
                    audio_length = sum(float(x) * (60 ** idx) for idx, x in enumerate(parts))
                else:
                    audio_length = 0.0

                inference_raw = str(row.get('Inference time (in sec)', '')).strip()
                if inference_raw.replace('.', '', 1).isdigit():
                    inference_time = float(inference_raw)
                elif ":" in inference_raw:
                    parts = list(reversed(inference_raw.split(":")))
                    inference_time = sum(float(x) * (60 ** idx) for idx, x in enumerate(parts))
                else:
                    inference_time = 0.0
