# Example API requests

Base URL (local dev): `http://localhost:8000`

## 1. Register + log in
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}'

TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
```

## 2. Upload a report
```bash
curl -X POST http://localhost:8000/api/reports/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@examples/sample_report.txt"
# => {"report_id": "REP-xxxxx", "status": "uploaded"}
```

## 3. Analyze it
```bash
curl -X POST http://localhost:8000/api/reports/REP-xxxxx/analyze \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Get findings
```bash
curl http://localhost:8000/api/reports/REP-xxxxx/findings \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Ask a question (RAG)
```bash
curl -X POST http://localhost:8000/api/reports/REP-xxxxx/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question":"Which values are outside the reference range?"}'
```

## 6. Historical comparison
```bash
curl http://localhost:8000/api/reports/REP-xxxxx/comparison \
  -H "Authorization: Bearer $TOKEN"
```
