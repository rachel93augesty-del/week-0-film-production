import json
import subprocess
import sys
import wave
from pathlib import Path


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
AUDIO_DIR = PROJECT_ROOT / "outputs" / "audio"

RADIO_CUT_DIR = PROJECT_ROOT / "outputs" / "radio_cut"

TEMP_AUDIO = RADIO_CUT_DIR / "radio_cut_audio.wav"
FINAL_OUTPUT = RADIO_CUT_DIR / "radio_cut.mp4"


# --------------------------------------------------
# Load storyboard
# --------------------------------------------------

def load_storyboard():
    with STORYBOARD_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# Measure WAV duration
# --------------------------------------------------

def get_wav_duration(path):
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()

        return frames / float(frame_rate)


# --------------------------------------------------
# Check FFmpeg
# --------------------------------------------------

def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )

    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: FFmpeg is not available.")
        print("Run: ffmpeg -version")
        sys.exit(1)


# --------------------------------------------------
# Build radio-cut audio timeline
# --------------------------------------------------

def build_audio_timeline(storyboard):

    inputs = []
    filters = []
    labels = []

    print("\nRadio-cut timing\n")

    print(
        f"{'Shot':<14}"
        f"{'Planned':>10}"
        f"{'Audio':>10}"
        f"{'Pause':>10}"
        f"{'Required':>12}"
    )

    print("-" * 56)

    for index, shot in enumerate(storyboard["shots"]):

        shot_id = shot["id"]

        planned_duration = float(
            shot["duration_seconds"]
        )

        # ------------------------------------------
        # Intentional pause
        # ------------------------------------------

        intentional_pause = float(
            shot.get("pause_after_seconds", 0)
        )

        # ------------------------------------------
        # Find narration file
        # ------------------------------------------

        audio_path = AUDIO_DIR / f"{shot_id}.wav"

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Missing narration file: {audio_path}"
            )

        # ------------------------------------------
        # Measure actual narration
        # ------------------------------------------

        actual_duration = get_wav_duration(
            audio_path
        )

        # ------------------------------------------
        # Calculate minimum duration required
        # ------------------------------------------

        minimum_required_duration = (
            actual_duration
            + intentional_pause
        )

        # ------------------------------------------
        # Safety check
        # ------------------------------------------

        if minimum_required_duration > planned_duration:

            raise ValueError(
                f"\n{shot_id}: timing does not fit.\n"
                f"Narration: {actual_duration:.2f}s\n"
                f"Requested pause: {intentional_pause:.2f}s\n"
                f"Minimum required: "
                f"{minimum_required_duration:.2f}s\n"
                f"Storyboard allows: "
                f"{planned_duration:.2f}s\n"
            )

        # ------------------------------------------
        # Fill remainder of shot with silence
        # ------------------------------------------

        pause_duration = (
            planned_duration
            - actual_duration
        )

        print(
            f"{shot_id:<14}"
            f"{planned_duration:>8.2f}s"
            f"{actual_duration:>8.2f}s"
            f"{pause_duration:>8.2f}s"
            f"{intentional_pause:>10.2f}s"
        )

        # ------------------------------------------
        # Add WAV file as FFmpeg input
        # ------------------------------------------

        inputs.extend([
            "-i",
            str(audio_path)
        ])

        # ------------------------------------------
        # Normalize and pad shot audio
        # ------------------------------------------

        label = f"a{index}"

        filters.append(
            f"[{index}:a]"
            f"aformat=sample_rates=24000:"
            f"channel_layouts=mono,"
            f"apad=pad_dur={pause_duration:.3f},"
            f"atrim=duration={planned_duration:.3f}"
            f"[{label}]"
        )

        labels.append(
            f"[{label}]"
        )

    # ----------------------------------------------
    # Concatenate shots in storyboard order
    # ----------------------------------------------

    concat_filter = (
        "".join(labels)
        + f"concat=n={len(labels)}:"
        f"v=0:a=1[outa]"
    )

    filters.append(
        concat_filter
    )

    return inputs, ";".join(filters)


# --------------------------------------------------
# Create continuous radio-cut WAV
# --------------------------------------------------

def create_radio_audio(storyboard):

    inputs, filter_graph = (
        build_audio_timeline(storyboard)
    )

    command = [
        "ffmpeg",
        "-y",

        *inputs,

        "-filter_complex",
        filter_graph,

        "-map",
        "[outa]",

        "-ar",
        "24000",

        "-ac",
        "1",

        str(TEMP_AUDIO)
    ]

    print(
        "\nCreating continuous narration timeline..."
    )

    subprocess.run(
        command,
        check=True
    )

    print(
        f"Audio timeline created: {TEMP_AUDIO}"
    )


# --------------------------------------------------
# Create black-screen MP4
# --------------------------------------------------

def create_black_screen_video(duration):

    command = [
        "ffmpeg",
        "-y",

        # Black 16:9 video
        "-f",
        "lavfi",

        "-i",
        "color=c=black:s=1920x1080:r=30",

        # Narration timeline
        "-i",
        str(TEMP_AUDIO),

        # Match storyboard duration
        "-t",
        str(duration),

        # Video codec
        "-c:v",
        "libx264",

        "-pix_fmt",
        "yuv420p",

        # Audio codec
        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        str(FINAL_OUTPUT)
    ]

    print(
        "\nCreating black-screen radio cut..."
    )

    subprocess.run(
        command,
        check=True
    )

    print(
        f"\nRadio cut saved to: {FINAL_OUTPUT}"
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\nBuilding radio cut...\n")

    # Confirm FFmpeg exists
    check_ffmpeg()

    # Load storyboard
    storyboard = load_storyboard()

    # Create output directory
    RADIO_CUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ----------------------------------------------
    # Calculate storyboard duration
    # ----------------------------------------------

    expected_duration = sum(
        float(shot["duration_seconds"])
        for shot in storyboard["shots"]
    )

    declared_duration = float(
        storyboard["project"][
            "target_duration_seconds"
        ]
    )

    # ----------------------------------------------
    # Check storyboard total
    # ----------------------------------------------

    if expected_duration != declared_duration:

        raise ValueError(
            "Storyboard timing mismatch: "
            f"shots total {expected_duration:.2f}s "
            f"but target_duration_seconds is "
            f"{declared_duration:.2f}s."
        )

    # ----------------------------------------------
    # Create narration timeline
    # ----------------------------------------------

    create_radio_audio(
        storyboard
    )

    # ----------------------------------------------
    # Measure assembled result
    # ----------------------------------------------

    assembled_duration = get_wav_duration(
        TEMP_AUDIO
    )

    print(
        f"\nAssembled narration timeline: "
        f"{assembled_duration:.2f} seconds"
    )

    # ----------------------------------------------
    # Create black-screen MP4
    # ----------------------------------------------

    create_black_screen_video(
        assembled_duration
    )

    # ----------------------------------------------
    # Final report
    # ----------------------------------------------

    print("\n--------------------------------")
    print("RADIO CUT COMPLETE")
    print("--------------------------------")

    print(
        f"Expected duration: "
        f"{expected_duration:.2f}s"
    )

    print(
        f"Actual duration:   "
        f"{assembled_duration:.2f}s"
    )

    print(
        f"Output: {FINAL_OUTPUT}"
    )


if __name__ == "__main__":
    main()