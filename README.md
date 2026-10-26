# Valora

## Start the Backend

Open a terminal:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Backend: http://localhost:8000  
API documentation: http://localhost:8000/docs

## Start the Frontend

Open a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Stop the Servers

Press `Ctrl + C` in each terminal to stop the servers.