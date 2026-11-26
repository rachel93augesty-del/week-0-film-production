import argparse
import base64
import io
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image


# -------------------------
# Paths and model
# -------------------------

ROOT = Path(__file__).resolve().parent.parent

STORYBOARD = ROOT / "storyboard.json"
REFERENCE = ROOT / "outputs" / "references" / "father_daughter_reference.png"
OUTPUT_DIR = ROOT / "outputs" / "keyframes"
RUNS_LOG = ROOT / "runs.jsonl"

MODEL = "gemini-nano-banana-2.1"


# -------------------------
# Load storyboard
# -------------------------

def load_storyboard():
    with STORYBOARD.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_shot(storyboard, shot_id):
    for shot in storyboard["shots"]:
        if shot["id"] == shot_id:
            return shot

    raise ValueError(f"Shot not found: {shot_id}")


# -------------------------
# Logging
# -------------------------

def log_run(record):
    with RUNS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# -------------------------
# Build prompt
# -------------------------

def build_prompt(shot):

    scene = shot["visual_prompt"]

    return f"""
Use the supplied image as the authoritative recurring-character reference.

Preserve the same two fictional recurring characters as closely as possible.

Adult character:
approximately 47 years old, same recognizable face,
clean short haircut, neat moustache only, no beard,
same apparent age and general build.

Child character:
approximately 9 to 10 years old, same recognizable face,
same apparent age, same dark braided hairstyle,
same natural child proportions.

Do not replace or substantially redesign either character.

Create this new scene:

{scene}

The film is set in Ethiopia around 2003-2004.

Use photorealistic cinematic realism, warm natural lighting,
realistic anatomy, natural skin texture, modest period-appropriate
clothing and ordinary environments.

Avoid modern smartphones, contemporary electronics,
modern fashion, cartoon styling, text, logos,
subtitles and watermarks.

Create one finished cinematic film frame.
Keep the important characters near the center so the image can
later support both 16:9 and 9:16 video framing.
"""


# -------------------------
# Generate image
# -------------------------

def generate(client, shot, force=False):

    shot_id = shot["id"]

    if shot_id == "end_card":
        raise ValueError("End card is created during assembly.")

    if not REFERENCE.exists():
        raise FileNotFoundError(
            f"Reference image not found: {REFERENCE}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{shot_id}.jpg"

    if output_path.exists() and not force:
        print(f"SKIP: {output_path.name} already exists.")
        print("Use --force to replace it.")
        return

    # Load reference image
    reference_bytes = REFERENCE.read_bytes()

    reference_part = types.Part.from_bytes(
        data=reference_bytes,
        mime_type="image/png"
    )

    prompt = build_prompt(shot)

    print(f"\nGenerating {shot_id}...")
    print(f"Model: {MODEL}")

    start = time.perf_counter()

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                reference_part,
                prompt
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )

        elapsed = time.perf_counter() - start

        saved = False

        for part in response.parts:

            if part.inline_data is None:
                continue

            data = part.inline_data.data

            if data is None:
                continue

            if isinstance(data, str):
                image_bytes = base64.b64decode(data)
            else:
                image_bytes = bytes(data)

            with Image.open(io.BytesIO(image_bytes)) as img:
                img.convert("RGB").save(
                    output_path,
                    "JPEG",
                    quality=95
                )

            saved = True
            break

        if not saved:
            raise RuntimeError(
                "Gemini returned no image."
            )

        log_run({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": "keyframe",
            "provider": "Google Gemini",
            "shot_id": shot_id,
            "model": MODEL,
            "status": "success",
            "latency_seconds": round(elapsed, 3),
            "output": str(output_path.relative_to(ROOT))
        })

        print("SUCCESS")
        print(f"Saved: {output_path}")
        print(f"Latency: {elapsed:.2f}s")

    except Exception as error:

        elapsed = time.perf_counter() - start

        log_run({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": "keyframe",
            "provider": "Google Gemini",
            "shot_id": shot_id,
            "model": MODEL,
            "status": "failed",
            "latency_seconds": round(elapsed, 3),
            "error": str(error)
        })

        print("\nGENERATION FAILED")
        print(error)

        raise


# -------------------------
# Main
# -------------------------

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--shot",
        required=True
    )

    parser.add_argument(
        "--force",
        action="store_true"
    )

    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    api_key = os.getenv("GEMINI_IMAGE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_IMAGE_API_KEY is missing from .env"
        )

    client = genai.Client(api_key=api_key)

    storyboard = load_storyboard()

    shot = find_shot(
        storyboard,
        args.shot
    )

    generate(
        client,
        shot,
        force=args.force
    )


if __name__ == "__main__":
    main()