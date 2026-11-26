import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "gemini_test"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "gemini_image_test.png"
)


# --------------------------------------------------
# Load Gemini API key
# --------------------------------------------------

load_dotenv(
    PROJECT_ROOT / ".env"
)

api_key = os.getenv(
    "GEMINI_API_KEY"
)

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from .env"
    )


# --------------------------------------------------
# Create Gemini client
# --------------------------------------------------

client = genai.Client(
    api_key=api_key
)


# --------------------------------------------------
# Very simple test prompt
# --------------------------------------------------

prompt = """
Create one photorealistic cinematic image of a quiet
early-2000s family sitting room.

Warm natural window light, ordinary furniture,
realistic photography, no people, no text,
no logos and no watermark-like lettering.
"""


print(
    "\nTesting Gemini image generation..."
)

print(
    "Model: gemini-nano-banana-2.1\n"
)


# --------------------------------------------------
# Generate image
# --------------------------------------------------

response = client.models.generate_content(
    model="gemini-nano-banana-2.1",
    contents=[prompt],
)


# --------------------------------------------------
# Create output directory
# --------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Find returned image
# --------------------------------------------------

image_saved = False

for part in response.parts:

    if part.text is not None:
        print(
            "Gemini text response:",
            part.text
        )

    elif part.inline_data is not None:

        image = part.as_image()

        image.save(
            OUTPUT_FILE
        )

        image_saved = True

        print(
            "SUCCESS"
        )

        print(
            f"Image saved to: {OUTPUT_FILE}"
        )


if not image_saved:

    raise RuntimeError(
        "Gemini responded but no image was returned."
    )