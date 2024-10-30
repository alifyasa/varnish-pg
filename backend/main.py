from fastapi import FastAPI, Request, Header
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import pytz
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/stats")
def stats(request: Request):
    headers = request.headers
    return {"headers": dict(headers), "currentTime": datetime.now()}


def random_pastel_color():
    """Generate a random pastel color."""
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return (r, g, b)


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

    # Create a square image with a random pastel color background
    img_size = 400  # Size of the image
    img = Image.new(
        "RGB", (img_size, img_size), color=random_pastel_color()
    )  # Random pastel color
    draw = ImageDraw.Draw(img)

    # Define a simple font
    font = ImageFont.load_default()

    # Calculate text size and position to center it using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    timestamp_bbox = draw.textbbox((0, 0), timestamp_text, font=font)

    # Centering the text
    text_position = (
        (img_size - (text_bbox[2] - text_bbox[0])) // 2,
        (img_size - (text_bbox[3] - text_bbox[1])) // 2 - 10,
    )
    timestamp_position = (
        (img_size - (timestamp_bbox[2] - timestamp_bbox[0])) // 2,
        (img_size - (timestamp_bbox[3] - timestamp_bbox[1])) // 2 + 10,
    )

    # Draw main text onto the image
    draw.text(text_position, text, fill=(0, 0, 0), font=font)

    # Draw timestamp onto the image
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
