mkcert 10.247.76.38 localhost 127.0.0.1

uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ../frontend/certs/key.pem --ssl-certfile ../frontend/certs/cert.pem
