from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def main(request: Request):
    headers = request.headers
    return {
        "headers": dict(headers),
        "currentTime": datetime.now()
    }
