from fastapi import FastAPI

app = FastAPI(title="Lumo Scheduler Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "scheduler-service", "status": "HEALTHY"}
