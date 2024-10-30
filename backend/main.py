from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import pytz

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
def generate_image(request: Request):
    # Determine the text to display on the image
    user_agent = (
        request.headers.get("X-UA-Device")
        or request.headers.get("User-Agent")
        or "Request has no user agent."
    )
    text = f"This image has been accessed from {user_agent}"

    # Get the current time in Jakarta
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    current_time = datetime.now(jakarta_tz).strftime("%Y-%m-%d %H:%M:%S")
    timestamp_text = f"Generated on: {current_time}"

    # Create an image with a better design
    img = Image.new("RGB", (400, 200), color=(240, 240, 240))  # Light gray background
    draw = ImageDraw.Draw(img)

    # Define a simple font
    font = ImageFont.load_default()

    # Define font sizes
    text_font_size = 16
    timestamp_font_size = 12

    # Draw main text onto the image
    text_position = (10, 70)
    draw.text(text_position, text, fill=(0, 0, 0), font=font)

    # Draw timestamp onto the image
    timestamp_position = (10, 120)
    draw.text(
        timestamp_position, timestamp_text, fill=(100, 100, 100), font=font
    )  # Dark gray for the timestamp

    # Save image to a buffer
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # Set response with Vary header
    response = StreamingResponse(buf, media_type="image/png")
    response.headers["Vary"] = "X-UA-Device"
    return response
