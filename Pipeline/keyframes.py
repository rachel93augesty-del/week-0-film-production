import argparse
import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
RUNS_LOG = PROJECT_ROOT / "runs.jsonl"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "keyframes"
)

REFERENCE_IMAGE = (
    PROJECT_ROOT
    / "outputs"
    / "references"
    / "father_daughter_reference.png"
)


# ============================================================
# Image model
# ============================================================

MODEL = "@cf/black-forest-labs/flux-2-dev"


# ============================================================
# Visual continuity instructions
# ============================================================

FATHER_REFERENCE = """
Use the adult character in the supplied reference image as the
authoritative visual identity baseline.

Preserve the same fictional recurring adult character as closely
as possible.

The approved character is approximately 47 years old.

Preserve:
- facial structure
- apparent age
- clean short haircut
- well-groomed moustache only
- no beard
- natural facial proportions
- body build
- overall recognizable appearance

For office or professional scenes, use neat early-2000s clothing:
a clean button-up shirt, understated jacket and suit trousers.

Do not redesign, beautify, culturally reinterpret, age, de-age,
or replace this character.
"""


DAUGHTER_REFERENCE = """
Use the child character in the supplied reference image as the
authoritative visual identity baseline.

Preserve the same fictional recurring child character as closely
as possible.

The approved character is approximately 9 to 10 years old.

Preserve:
- facial structure
- apparent age
- hairstyle
- hair length
- simple braid
- child body proportions
- overall recognizable appearance

For outside and office scenes, use a simple modest knee-length
everyday dress appropriate to Ethiopia around 2003-2004.

For home scenes, use simple trousers and an ordinary comfortable top.

Do not redesign, beautify, age, de-age, culturally reinterpret,
or replace this character.
"""


STYLE_REFERENCE = """
Photorealistic cinematic realism.

Setting: Ethiopia around 2003-2004.

Use:
- warm natural lighting
- realistic skin texture
- realistic anatomy
- ordinary family and office environments
- modest early-2000s clothing
- period-appropriate furniture and surroundings
- natural color palette
- subtle nostalgia
- restrained cinematic photography

Avoid:
- smartphones
- wireless earbuds
- contemporary electronics
- modern ultra-thin laptops
- contemporary fashion
- luxury interiors
- exaggerated cultural styling
- cartoon appearance
- fantasy appearance
- artificial sepia filters
- artificial vintage damage
- exaggerated expressions
- logos
- captions
- subtitles
- visible text
- watermarks
"""


# ============================================================
# Load private credentials
# ============================================================

def load_credentials():

    load_dotenv(
        PROJECT_ROOT / ".env"
    )

    account_id = os.getenv(
        "CLOUDFLARE_ACCOUNT_ID"
    )

    api_token = os.getenv(
        "CLOUDFLARE_API_TOKEN"
    )

    if not account_id:
        raise RuntimeError(
            "CLOUDFLARE_ACCOUNT_ID is missing from .env"
        )

    if not api_token:
        raise RuntimeError(
            "CLOUDFLARE_API_TOKEN is missing from .env"
        )

    return account_id, api_token


# ============================================================
# Load storyboard
# ============================================================

def load_storyboard():

    with STORYBOARD_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# Find one shot
# ============================================================

def find_shot(
    storyboard,
    shot_id
):

    for shot in storyboard["shots"]:

        if shot["id"] == shot_id:
            return shot

    raise ValueError(
        f"Shot '{shot_id}' was not found in storyboard.json"
    )


# ============================================================
# Build strong reference-preservation prompt
# ============================================================

def build_prompt(shot):

    if "visual_prompt" not in shot:

        raise ValueError(
            f"{shot['id']} does not contain visual_prompt."
        )

    scene = shot["visual_prompt"]

    prompt = f"""
IMAGE EDITING TASK:

The supplied father-and-daughter image is the authoritative
visual identity reference for this film.

Preserve the two fictional characters from the reference image
as closely as possible.

Do not generate substitute people.

Do not reinterpret the recurring characters.

The goal is to place the SAME recurring fictional characters into
a new cinematic scene.


ADULT CHARACTER:

{FATHER_REFERENCE}


CHILD CHARACTER:

{DAUGHTER_REFERENCE}


SHOT REQUIREMENT:

{scene}


CHANGES ALLOWED:

You may change:
- pose
- body position
- camera framing
- camera angle
- environment
- scene action
- period-appropriate clothing when required by the scene
- lighting appropriate to the shot


CHANGES NOT ALLOWED:

Do not significantly change:
- recurring facial identity
- apparent age
- facial proportions
- hairstyle
- moustache
- recognizable character appearance
- child age or body proportions


RELATIONSHIP CONTINUITY:

The generated frame must clearly depict the same recurring pair
shown in the supplied reference image.

Preserve visual continuity between the two characters.

Do not create two unrelated-looking substitute characters.


PERIOD AND CINEMATIC STYLE:

{STYLE_REFERENCE}


OUTPUT REQUIREMENT:

Create one photorealistic cinematic film frame.

The image should look like a still frame from a realistic family
memory rather than a posed studio portrait.

Keep visual attention on the recurring characters.

Do not place any written text, captions, subtitles, logos,
watermarks or labels inside the image.

The supplied image contains fictional characters and is the
approved identity baseline for this project.
"""

    return " ".join(
        prompt.split()
    )


# ============================================================
# Append record to runs.jsonl
# ============================================================

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


# ============================================================
# Generate one keyframe
# ============================================================

def generate_keyframe(
    account_id,
    api_token,
    shot,
    force=False
):

    shot_id = shot["id"]

    # --------------------------------------------
    # Do not generate AI-disclosure card here
    # --------------------------------------------

    if shot.get("visual_type") == "ai_disclosure":

        raise ValueError(
            "The AI disclosure card is not an AI-generated keyframe."
        )

    # --------------------------------------------
    # Ensure output directory exists
    # --------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_DIR
        / f"{shot_id}.jpg"
    )

    # --------------------------------------------
    # Cache
    # --------------------------------------------

    if (
        output_path.exists()
        and not force
    ):

        print(
            f"SKIP: {output_path.name} already exists."
        )

        print(
            "Use --force to intentionally regenerate it."
        )

        return

    # --------------------------------------------
    # Reference-image check
    # --------------------------------------------

    if not REFERENCE_IMAGE.exists():

        raise FileNotFoundError(
            "Approved reference image was not found:\n"
            f"{REFERENCE_IMAGE}"
        )

    # --------------------------------------------
    # Build prompt
    # --------------------------------------------

    prompt = build_prompt(
        shot
    )

    # --------------------------------------------
    # Cloudflare endpoint
    # --------------------------------------------

    url = (
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{account_id}/"
        f"ai/run/{MODEL}"
    )

    # Do NOT manually set multipart Content-Type.
    headers = {
        "Authorization":
            f"Bearer {api_token}"
    }

    print(
        f"\nGenerating keyframe for {shot_id}..."
    )

    print(
        f"Model: {MODEL}"
    )

    print(
        f"Reference image: {REFERENCE_IMAGE.name}"
    )

    start_time = (
        time.perf_counter()
    )

    try:

        # ----------------------------------------
        # Open approved reference image
        # ----------------------------------------

        with REFERENCE_IMAGE.open(
            "rb"
        ) as reference_file:

            form_data = {
                "prompt": prompt
            }

            files = {
                "image": (
                    REFERENCE_IMAGE.name,
                    reference_file,
                    "image/png"
                )
            }

            # ------------------------------------
            # FLUX.2 Dev request
            # ------------------------------------

            response = requests.post(
                url,
                headers=headers,
                data=form_data,
                files=files,
                timeout=180
            )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        # ----------------------------------------
        # Print useful Cloudflare error response
        # ----------------------------------------

        if not response.ok:

            print(
                "\nCloudflare response:"
            )

            print(
                response.text
            )

            response.raise_for_status()

        # ----------------------------------------
        # Parse response
        # ----------------------------------------

        data = response.json()

        if not data.get("success"):

            raise RuntimeError(
                "Cloudflare returned success=false:\n"
                f"{data}"
            )

        result = data.get(
            "result",
            {}
        )

        image_base64 = result.get(
            "image"
        )

        if not image_base64:

            raise RuntimeError(
                "Cloudflare request succeeded but "
                "result.image was missing."
            )

        #  ----------------------------------------
        # Decode image
        # ----------------------------------------

        image_bytes = (
            base64.b64decode(
                image_base64
            )
        )

        # ---------------------------------------
        # Save image
        # ----------------------------------------

        with output_path.open(
            "wb"
        ) as image_file:

            image_file.write(
                image_bytes
            )

        # ----------------------------------------
        # Log successful model call
        # ----------------------------------------

        log_run({
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "stage": "keyframe",

            "shot_id": shot_id,

            "model": MODEL,

            "reference_image": str(
                REFERENCE_IMAGE.relative_to(
                    PROJECT_ROOT
                )
            ),

            "status": "success",

            "latency_seconds": round(
                elapsed,
                3
            ),

            "output": str(
                output_path.relative_to(
                    PROJECT_ROOT
                )
            )
        })

        print(
            "\nSUCCESS"
        )

        print(
            f"Image saved to: "
            f"{output_path}"
        )

        print(
            f"Generation latency: "
            f"{elapsed:.2f} seconds"
        )

    except Exception as error:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        # ----------------------------------------
        # Log failure
        # ----------------------------------------

        log_run({
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "stage": "keyframe",

            "shot_id": shot_id,

            "model": MODEL,

            "reference_image": str(
                REFERENCE_IMAGE.relative_to(
                    PROJECT_ROOT
                )
            ),

            "status": "failed",

            "latency_seconds": round(
                elapsed,
                3
            ),

            "error": str(
                error
            )
        })

        print(
            "\nGENERATION FAILED"
        )

        print(
            error
        )

        raise


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate one reference-conditioned "
            "film keyframe using FLUX.2 Dev."
        )
    )

    parser.add_argument(
        "--shot",
        required=True,
        help=(
            "Storyboard shot ID. "
            "Example: shot_01"
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Regenerate the image even when "
            "a cached keyframe already exists."
        )
    )

    args = parser.parse_args()

    # Load credentials
    account_id, api_token = (
        load_credentials()
    )

    # Load storyboard
    storyboard = (
        load_storyboard()
    )

    # Find requested shot
    shot = find_shot(
        storyboard,
        args.shot
    )

    # Generate
    generate_keyframe(
        account_id,
        api_token,
        shot,
        force=args.force
    )


if __name__ == "__main__":
    main()