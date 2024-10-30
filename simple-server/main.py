from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from typing import Union

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/stats")
def stats(request: Request):
    headers = request.headers
    return {"headers": dict(headers), "currentTime": datetime.now()}


@app.get("/generate-image")
def generate_image(request: Request, x_ua_device: str = Header(None)):
    # Determine the text to display on the image
    user_agent = (
        x_ua_device or request.headers.get("User-Agent") or "Request has no user agent."
    )
    text = f"This image has been accessed from {user_agent}"

    # Create an image
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Define a simple font
    font = ImageFont.load_default()

    # Draw text onto the image
    text_position = (10, 90)
    draw.text(text_position, text, fill=(0, 0, 0), font=font)

    # Save image to a buffer
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # Set response with Vary header
    response = StreamingResponse(buf, media_type="image/png")
    response.headers["Vary"] = "X-UA-Device"
    return response
