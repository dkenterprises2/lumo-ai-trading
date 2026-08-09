from fastapi import FastAPI

app = FastAPI(title="Lumo API Gateway Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "api-gateway", "status": "HEALTHY"}

@app.get("/")
def read_root():
    return {"message": "Lumo API Gateway & Edge Router v2.8.0"}
