curl -X 'POST' \
  'http://127.0.0.1:8000/apps/api/benchmarks/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@benchmarking_latest_file.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
