curl -X 'POST' \
  'http://127.0.0.1:8000/api/benchmarks/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@asr_benchmarking_Q2_2025 (1).xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
