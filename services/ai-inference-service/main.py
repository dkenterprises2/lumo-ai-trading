from fastapi import FastAPI

app = FastAPI(title="Lumo AI Inference Microservice", version="2.8.0")

@app.get("/health")
def health_check():
    return {"service": "ai-inference-service", "status": "HEALTHY"}
