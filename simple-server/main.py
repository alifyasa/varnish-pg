from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/hello")
async def hello(request: Request):
    headers = request.headers
    body = await request.body()
    return {
        "headers": dict(headers),
        "body": body.decode("utf-8")
    }
