from fastapi import FastAPI

app = FastAPI(title="Lumo Analytics Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "analytics-service", "status": "HEALTHY"}
