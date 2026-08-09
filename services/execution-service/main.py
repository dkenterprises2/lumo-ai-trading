from fastapi import FastAPI

app = FastAPI(title="Lumo Execution Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "execution-service", "status": "HEALTHY"}
