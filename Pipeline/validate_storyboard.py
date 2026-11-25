import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


# ---------------------------------------
# Locate project files
# ---------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
SCHEMA_PATH = PROJECT_ROOT / "schema" / "storyboard.schema.json"


# ---------------------------------------
# Load JSON file
# ---------------------------------------

def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    except json.JSONDecodeError as error:
        print(f"ERROR: Invalid JSON in {path.name}")
        print(f"Line {error.lineno}, column {error.colno}: {error.msg}")
        sys.exit(1)


# ---------------------------------------
# Validate against JSON Schema
# ---------------------------------------

def validate_schema(storyboard, schema):
    validator = Draft202012Validator(schema)

    errors = sorted(
        validator.iter_errors(storyboard),
        key=lambda error: list(error.path)
    )

    if errors:
        print("\nSCHEMA VALIDATION FAILED\n")

        for error in errors:
            location = ".".join(str(part) for part in error.path)

            if not location:
                location = "root"

            print(f"- {location}: {error.message}")

        return False

    print("Schema validation passed.")
    return True


# ---------------------------------------
# Check shot IDs
# ---------------------------------------

def validate_unique_ids(storyboard):
    shot_ids = [shot["id"] for shot in storyboard["shots"]]

    duplicates = {
        shot_id
        for shot_id in shot_ids
        if shot_ids.count(shot_id) > 1
    }

    if duplicates:
        print(
            "ERROR: Duplicate shot IDs found:",
            ", ".join(sorted(duplicates))
        )
        return False

    print(f"Shot ID check passed: {len(shot_ids)} unique entries.")
    return True


# ---------------------------------------
# Check total film duration
# ---------------------------------------

def validate_duration(storyboard):
    shots = storyboard["shots"]

    total_duration = sum(
        shot["duration_seconds"]
        for shot in shots
    )

    declared_duration = storyboard["project"]["target_duration_seconds"]

    print(f"Calculated film duration: {total_duration} seconds.")
    print(f"Declared target duration: {declared_duration} seconds.")

    valid = True

    if total_duration < 60:
        print("ERROR: Film is shorter than 60 seconds.")
        valid = False

    if total_duration > 90:
        print("ERROR: Film is longer than 90 seconds.")
        valid = False

    if total_duration != declared_duration:
        print(
            "ERROR: target_duration_seconds does not match "
            "the calculated shot duration."
        )
        valid = False

    if valid:
        print("Duration check passed.")

    return valid


# ---------------------------------------
# Check required aspect ratios
# ---------------------------------------

def validate_aspect_ratios(storyboard):
    aspect_ratios = storyboard["project"]["aspect_ratios"]

    required = {"16:9", "9:16"}
    actual = set(aspect_ratios)

    missing = required - actual

    if missing:
        print(
            "ERROR: Missing required aspect ratio(s):",
            ", ".join(sorted(missing))
        )
        return False

    print("Aspect-ratio check passed: 16:9 and 9:16.")
    return True


# ---------------------------------------
# Check AI disclosure
# ---------------------------------------

def validate_ai_disclosure(storyboard):
    end_cards = [
        shot
        for shot in storyboard["shots"]
        if shot.get("visual_type") == "ai_disclosure"
    ]

    if not end_cards:
        print("ERROR: No AI disclosure end card found.")
        return False

    if len(end_cards) > 1:
        print("ERROR: More than one AI disclosure card found.")
        return False

    disclosure = end_cards[0]

    if not disclosure.get("on_screen_text", "").strip():
        print("ERROR: AI disclosure has no on-screen text.")
        return False

    if not disclosure.get("narration_amharic", "").strip():
        print("ERROR: AI disclosure has no Amharic narration.")
        return False

    print("AI disclosure check passed.")
    return True


# ---------------------------------------
# Main validation
# ---------------------------------------

def main():
    print("\nValidating film storyboard...\n")

    storyboard = load_json(STORYBOARD_PATH)
    schema = load_json(SCHEMA_PATH)

    checks = [
        validate_schema(storyboard, schema)
    ]

    # Only continue if the structure itself is valid.
    if not checks[0]:
        print("\nStoryboard validation FAILED.")
        sys.exit(1)

    checks.extend([
        validate_unique_ids(storyboard),
        validate_duration(storyboard),
        validate_aspect_ratios(storyboard),
        validate_ai_disclosure(storyboard),
    ])

    if all(checks):
        print("\n--------------------------------")
        print("STORYBOARD VALIDATION PASSED")
        print("--------------------------------")
        print("The storyboard is ready for the next pipeline stage.")
        sys.exit(0)

    print("\n--------------------------------")
    print("STORYBOARD VALIDATION FAILED")
    print("--------------------------------")
    print("Fix the errors above and run validation again.")
    sys.exit(1)


if __name__ == "__main__":
    main()