from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def get_health():
    return {"status": "healthy", "database": None, "ready": True},
