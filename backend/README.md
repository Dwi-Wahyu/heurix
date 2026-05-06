uvicorn main:app --reload --host 0.0.0.0 --port 8000

uvicorn main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile ../frontend/certs/key.pem --ssl-certfile ../frontend/certs/cert.pem
