from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Linguacast")

# Connect your route(s)
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Linguacast is running"}
