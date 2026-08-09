from fastapi import FastAPI

app = FastAPI(title="Lumo Trading Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "trading-service", "status": "HEALTHY"}
