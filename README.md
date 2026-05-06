mkcert -key-file key.pem -cert-file cert.pem 10.131.121.38 localhost 127.0.0.1

mkdir frontend/certs

mv key.pem frontend/certs/key.pem && mv cert.pem frontend/certs/cert.pem

cd backend

python3 -m venv venv

source venv/Bin/Activate

uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile frontend/certs/key.pem --ssl-certfile frontend/certs/cert.pem

uvicorn main:app --reload --host 0.0.0.0 --port 8000

cd ../frontend

bun i

bun dev
