import argparse
import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# --------------------------------------------------
# Project paths and configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "audio"
RUNS_LOG = PROJECT_ROOT / "runs.jsonl"

MODEL = "gemini-3.8-flash-tts"
VOICE = "Kore"


# --------------------------------------------------
# Load storyboard
# --------------------------------------------------

def load_storyboard():
    with STORYBOARD_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# Load private Gemini API key
# --------------------------------------------------

def load_api_key():
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found. "
            "Add the key to your private .env file."
        )

    return api_key


# --------------------------------------------------
# Find requested storyboard shot
# --------------------------------------------------

def find_shot(storyboard, shot_id):
    for shot in storyboard["shots"]:
        if shot["id"] == shot_id:
            return shot

    raise ValueError(
        f"Shot '{shot_id}' was not found in storyboard.json"
    )


# --------------------------------------------------
# Log every model call to runs.jsonl
# --------------------------------------------------

def log_run(record):
    with RUNS_LOG.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(record, ensure_ascii=False) + "\n"
        )


# --------------------------------------------------
# Generate narration
# --------------------------------------------------

def generate_narration(client, shot, force=False):

    shot_id = shot["id"]
    narration = shot["narration_amharic"]

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = OUTPUT_DIR / f"{shot_id}.wav"

    # ----------------------------------------------
    # Basic cache
    # ----------------------------------------------

    if output_path.exists() and not force:
        print(
            f"SKIP: {output_path.name} already exists."
        )
        print(
            "Use --force if you intentionally want "
            "to regenerate this narration."
        )
        return

    print(f"\nGenerating narration for {shot_id}...\n")
    print(f"Text: {narration}\n")

    start_time = time.perf_counter()

    try:

        # ------------------------------------------
        # Gemini TTS request
        # ------------------------------------------

        response = client.interactions.create(
            model=MODEL,

            input=[
                {
                    "type": "user_input",
                    "content": [
                        {
                            "type": "text",
                            "text": narration,
                            "annotations": [
                                {
                                    "type": "speech_metadata",
                                    "style": (
                                        "Warm, gentle and reflective "
                                        "storytelling. Speak naturally "
                                        "in Amharic at a calm pace, "
                                        "as an adult remembering a loving "
                                        "childhood memory about her father."
                                    )
                                }
                            ]
                        }
                    ]
                }
            ],

            response_format={
                "type": "audio"
            },

            generation_config={
                "speech_config": [
                    {
                        "voice": VOICE
                    }
                ]
            }
        )

        elapsed = time.perf_counter() - start_time

        # ------------------------------------------
        # Get returned audio
        # ------------------------------------------

        audio_bytes = base64.b64decode(
            response.output_audio.data
        )

        # ------------------------------------------
        # Save WAV
        # ------------------------------------------

        with output_path.open("wb") as audio_file:
            audio_file.write(audio_bytes)

        # ------------------------------------------
        # Log successful model call
        # ------------------------------------------

        log_run({
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "stage": "narration",
            "shot_id": shot_id,
            "model": MODEL,
            "voice": VOICE,
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

        print("SUCCESS")
        print(
            f"Audio saved to: {output_path}"
        )
        print(
            f"Generation latency: "
            f"{elapsed:.2f} seconds"
        )

    except Exception as error:

        elapsed = time.perf_counter() - start_time

        # ------------------------------------------
        # Log failed model call
        # ------------------------------------------

        log_run({
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "stage": "narration",
            "shot_id": shot_id,
            "model": MODEL,
            "voice": VOICE,
            "status": "failed",

            "latency_seconds": round(
                elapsed,
                3
            ),

            "error": str(error)
        })

        print("\nGENERATION FAILED\n")
        print(error)

        raise


# --------------------------------------------------
# Program entry point
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate Amharic narration "
            "for one storyboard shot."
        )
    )

    parser.add_argument(
        "--shot",
        required=True,
        help="Storyboard shot ID, for example shot_01"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Regenerate narration even when "
            "an output file already exists."
        )
    )

    args = parser.parse_args()

    # Load storyboard
    storyboard = load_storyboard()

    # Find requested shot
    shot = find_shot(
        storyboard,
        args.shot
    )

    # Load private API key
    api_key = load_api_key()

    # Connect to Gemini
    client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        api_version="v1beta"
    )
)

    # Generate narration
    generate_narration(
        client,
        shot,
        force=args.force
    )


if __name__ == "__main__":
    main()