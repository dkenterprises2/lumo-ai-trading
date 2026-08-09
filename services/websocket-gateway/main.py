from fastapi import FastAPI

app = FastAPI(title="Lumo WebSocket Gateway Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "websocket-gateway", "status": "HEALTHY"}
