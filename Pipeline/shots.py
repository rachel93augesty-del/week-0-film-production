import json
import subprocess
import sys
from pathlib import Path


# ============================================================
# Paths
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

STORYBOARD_PATH = ROOT / "storyboard.json"
KEYFRAME_DIR = ROOT / "outputs" / "keyframes"
OUTPUT_DIR = ROOT / "outputs" / "shots"


# ============================================================
# Motion design
# ============================================================

MOTION = {
    "shot_01": "push_in",
    "shot_02": "pan_right",
    "shot_03": "push_in",
    "shot_04": "push_in",
    "shot_05": "push_in",
    "shot_06": "subtle_push",
    "shot_07": "near_static",
    "shot_08": "slow_push",
    "shot_09": "warm_push",
    "shot_10": "near_static",
    "shot_11": "pull_back",
}


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
# Check FFmpeg
# ============================================================

def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except Exception:
        print("ERROR: FFmpeg is not available.")
        sys.exit(1)


# ============================================================
# FFmpeg motion filters
# ============================================================

def get_motion_filter(motion, duration, fps=30):

    frames = int(duration * fps)

    # Square image -> 16:9.
    # Scale large first so camera movement can happen
    # without exposing empty edges.

    base = (
        "scale=2200:2200,"
    )

    if motion == "push_in":

        zoom = (
            f"zoompan="
            f"z='min(zoom+0.0007,1.08)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    elif motion == "slow_push":

        zoom = (
            f"zoompan="
            f"z='min(zoom+0.00045,1.06)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    elif motion == "warm_push":

        zoom = (
            f"zoompan="
            f"z='min(zoom+0.0009,1.09)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    elif motion == "subtle_push":

        zoom = (
            f"zoompan="
            f"z='min(zoom+0.0003,1.035)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    elif motion == "near_static":

        zoom = (
            f"zoompan="
            f"z='min(zoom+0.00015,1.02)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    elif motion == "pull_back":

        # Start a little closer and slowly pull away.
        zoom = (
            f"zoompan="
            f"z='if(eq(on,0),1.08,max(zoom-0.00035,1.01))':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    elif motion == "pan_right":

        # Very slow lateral movement.
        zoom = (
            f"zoompan="
            f"z='1.07':"
            f"x='min((iw-iw/zoom)*on/{frames},"
            f"iw-iw/zoom)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    else:

        zoom = (
            f"zoompan="
            f"z='1.02':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={frames}:"
            f"s=1920x1080:"
            f"fps={fps}"
        )

    return base + zoom


# ============================================================
# Generate one shot
# ============================================================

def generate_shot(shot, force=False):

    shot_id = shot["id"]

    # End card is created later.
    if shot_id == "end_card":
        return

    image_path = (
        KEYFRAME_DIR / f"{shot_id}.jpg"
    )

    output_path = (
        OUTPUT_DIR / f"{shot_id}.mp4"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing keyframe: {image_path}"
        )

    if output_path.exists() and not force:
        print(
            f"SKIP: {output_path.name} already exists."
        )
        return

    duration = float(
        shot["duration_seconds"]
    )

    motion = MOTION.get(
        shot_id,
        "near_static"
    )

    vf = get_motion_filter(
        motion,
        duration
    )

    print(
        f"Creating {shot_id}: "
        f"{duration:.1f}s | {motion}"
    )

    command = [
        "ffmpeg",
        "-y",

        "-loop",
        "1",

        "-i",
        str(image_path),

        "-vf",
        vf,

        "-t",
        str(duration),

        "-r",
        "30",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "18",

        "-pix_fmt",
        "yuv420p",

        "-an",

        str(output_path)
    ]

    subprocess.run(
        command,
        check=True
    )


# ============================================================
# Main
# ============================================================

def main():

    force = "--force" in sys.argv

    check_ffmpeg()

    storyboard = load_storyboard()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nCreating cinematic shot clips...\n"
    )

    for shot in storyboard["shots"]:
        generate_shot(
            shot,
            force=force
        )

    print(
        "\nSHOT GENERATION COMPLETE"
    )

    print(
        f"Output folder: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()