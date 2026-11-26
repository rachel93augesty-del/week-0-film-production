import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# ----------------------------------------
# Paths
# ----------------------------------------

ROOT = Path(__file__).resolve().parent.parent

STORYBOARD = ROOT / "storyboard.json"

REFERENCE = (
    ROOT
    / "outputs"
    / "references"
    / "father_daughter_reference.png"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "keyframes"
)

RUNS_LOG = ROOT / "runs.jsonl"


# ----------------------------------------
# fal.ai model
# ----------------------------------------

MODEL = "blackforestlabs/flux-3/edit-image"

FAL_URL = (
    f"https://fal.run/{MODEL}"
)


# ----------------------------------------
# Load storyboard
# ----------------------------------------

def load_storyboard():

    with STORYBOARD.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def find_shot(storyboard, shot_id):

    for shot in storyboard["shots"]:

        if shot["id"] == shot_id:
            return shot

    raise ValueError(
        f"Shot not found: {shot_id}"
    )


# ----------------------------------------
# Logging
# ----------------------------------------

def log_run(record):

    with RUNS_LOG.open(
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )


# ----------------------------------------
# Prompt
# ----------------------------------------

def build_prompt(shot):

    scene = shot["visual_prompt"]

    return f"""
Use the supplied reference image as the authoritative
visual identity reference.

Preserve the same two recurring fictional characters
as closely as possible.

Adult recurring character:
approximately 47 years old,
same recognizable facial structure,
clean short haircut,
neat moustache only,
no beard,
same apparent age and build.

Child recurring character:
approximately 9 to 10 years old,
same recognizable facial structure,
same apparent age,
same braided dark hairstyle,
same natural child proportions.

Do not replace the recurring characters with new people.

Create this scene:

{scene}

Setting:
Ethiopia around 2003-2004.

Style:
photorealistic cinematic film frame,
warm natural lighting,
realistic anatomy,
natural textures,
modest period-appropriate clothing
and ordinary environments.

Avoid:
modern smartphones,
modern electronics,
contemporary fashion,
cartoon styling,
text,
logos,
subtitles,
watermarks.

Keep the important subjects near the center
so the image can later support both
16:9 and 9:16 framing.

Generate one finished cinematic image.
"""


# ----------------------------------------
# Upload reference image to fal storage
# ----------------------------------------

def upload_reference(api_key):

    upload_url = (
        "https://fal.run/fal-ai/"
        "fast-sdxl/upload"
    )

    headers = {
        "Authorization": f"Key {api_key}"
    }

    with REFERENCE.open("rb") as file:

        files = {
            "file": (
                REFERENCE.name,
                file,
                "image/png"
            )
        }

        response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            timeout=120
        )

    if not response.ok:

        print(
            "\nReference upload failed:"
        )

        print(response.text)

        response.raise_for_status()

    data = response.json()

    reference_url = (
        data.get("url")
        or data.get("file_url")
    )

    if not reference_url:

        raise RuntimeError(
            "Reference upload succeeded "
            "but no URL was returned."
        )

    return reference_url


# ----------------------------------------
# Generate keyframe
# ----------------------------------------

def generate(
    api_key,
    shot,
    force=False
):

    shot_id = shot["id"]

    if shot_id == "end_card":

        raise ValueError(
            "End card is created during assembly."
        )

    if not REFERENCE.exists():

        raise FileNotFoundError(
            f"Reference image missing: "
            f"{REFERENCE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR
        / f"{shot_id}.jpg"
    )

    # Cache
    if (
        output_path.exists()
        and not force
    ):

        print(
            f"SKIP: {output_path.name} "
            "already exists."
        )

        print(
            "Use --force to replace it."
        )

        return

    print(
        f"\nGenerating {shot_id} "
        "with fal.ai..."
    )

    print(
        f"Model: {MODEL}"
    )

    start = time.perf_counter()

    try:

        # Upload reference
        print(
            "Uploading reference image..."
        )

        reference_url = (
            upload_reference(api_key)
        )

        prompt = (
            build_prompt(shot)
        )

        headers = {
            "Authorization":
                f"Key {api_key}",

            "Content-Type":
                "application/json"
        }

        payload = {
            "prompt": prompt,

            "image_urls": [
                reference_url
            ],

            "image_size": {
                "width": 1280,
                "height": 720
            },

            "num_images": 1,

            "output_format": "jpeg"
        }

        response = requests.post(
            FAL_URL,
            headers=headers,
            json=payload,
            timeout=180
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        if not response.ok:

            print(
                "\nfal.ai response:"
            )

            print(
                response.text
            )

            response.raise_for_status()

        data = response.json()

        images = data.get(
            "images",
            []
        )

        if not images:

            raise RuntimeError(
                "fal.ai returned no images."
            )

        image_url = (
            images[0].get("url")
        )

        if not image_url:

            raise RuntimeError(
                "Generated image URL missing."
            )

        # Download generated image
        image_response = requests.get(
            image_url,
            timeout=120
        )

        image_response.raise_for_status()

        output_path.write_bytes(
            image_response.content
        )

        # Log successful call
        log_run({
            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "stage":
                "keyframe",

            "provider":
                "fal.ai",

            "shot_id":
                shot_id,

            "model":
                MODEL,

            "status":
                "success",

            "latency_seconds":
                round(
                    elapsed,
                    3
                ),

            "output":
                str(
                    output_path.relative_to(
                        ROOT
                    )
                )
        })

        print(
            "\nSUCCESS"
        )

        print(
            f"Saved: {output_path}"
        )

        print(
            f"Latency: "
            f"{elapsed:.2f}s"
        )

    except Exception as error:

        elapsed = (
            time.perf_counter()
            - start
        )

        log_run({
            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "stage":
                "keyframe",

            "provider":
                "fal.ai",

            "shot_id":
                shot_id,

            "model":
                MODEL,

            "status":
                "failed",

            "latency_seconds":
                round(
                    elapsed,
                    3
                ),

            "error":
                str(error)
        })

        print(
            "\nGENERATION FAILED"
        )

        print(
            error
        )

        raise


# ----------------------------------------
# Main
# ----------------------------------------

def main():

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "--shot",
        required=True
    )

    parser.add_argument(
        "--force",
        action="store_true"
    )

    args = parser.parse_args()

    # Load API key
    load_dotenv(
        ROOT / ".env"
    )

    api_key = (
        os.getenv("FAL_KEY")
    )

    if not api_key:

        raise RuntimeError(
            "FAL_KEY is missing from .env"
        )

    storyboard = (
        load_storyboard()
    )

    shot = find_shot(
        storyboard,
        args.shot
    )

    generate(
        api_key,
        shot,
        force=args.force
    )


if __name__ == "__main__":
    main()