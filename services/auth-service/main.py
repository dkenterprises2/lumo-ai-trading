from fastapi import FastAPI

app = FastAPI(title="Lumo Auth Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "auth-service", "status": "HEALTHY"}
