import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "pipeline"

AUDIO_DIR = ROOT / "outputs" / "audio"
KEYFRAME_DIR = ROOT / "outputs" / "keyframes"
MUSIC_FILE = ROOT / "outputs" / "music" / "final_music.wav"

FINAL_FILE = (
    ROOT
    / "outputs"
    / "final"
    / "father_care_16x9.mp4"
)


def run_stage(name, script):
    print("\n" + "=" * 60)
    print(f"STAGE: {name}")
    print("=" * 60)

    subprocess.run(
        [
            sys.executable,
            str(PIPELINE / script)
        ],
        cwd=ROOT,
        check=True
    )


def check_assets():
    print("\nChecking required production assets...")

    missing = []

    # Check narration for Shots 1-11.
    # end_card.wav is intentionally NOT required.
    for number in range(1, 12):
        path = AUDIO_DIR / f"shot_{number:02}.wav"

        if not path.exists():
            missing.append(path)

    # Check keyframes for Shots 1-11.
    for number in range(1, 12):
        path = KEYFRAME_DIR / f"shot_{number:02}.jpg"

        if not path.exists():
            missing.append(path)

    # Check final soundtrack.
    if not MUSIC_FILE.exists():
        missing.append(MUSIC_FILE)

    if missing:
        print("\nERROR: Required assets are missing:")

        for path in missing:
            print(f"- {path.relative_to(ROOT)}")

        print(
            "\nGenerate or restore the missing assets "
            "before running the final pipeline."
        )

        sys.exit(1)

    print("All required production assets found.")


def main():
    print("\n================================")
    print("FOR ME, MY FATHER WAS CARE")
    print("FILM PIPELINE")
    print("================================")

    # 1. Validate storyboard.
    run_stage(
        "Validate storyboard",
        "validate_storyboard.py"
    )

    # 2. Verify expensive/generated assets exist.
    check_assets()

    # 3. Convert keyframes into motion clips.
    run_stage(
        "Create cinematic motion clips",
        "shots.py"
    )

    # 4. Generate English subtitle file.
    run_stage(
        "Generate English subtitles",
        "subtitles.py"
    )

    # 5. Assemble final film.
    run_stage(
        "Assemble final 16:9 film",
        "assemble.py"
    )

    if not FINAL_FILE.exists():
        raise RuntimeError(
            "Pipeline finished but final film "
            "was not found."
        )

    print("\n================================")
    print("PIPELINE COMPLETE")
    print("================================")

    print("\nFinal film:")
    print(FINAL_FILE)


if __name__ == "__main__":
    main()