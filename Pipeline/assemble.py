import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

STORYBOARD = ROOT / "storyboard.json"

SHOTS_DIR = ROOT / "outputs" / "shots"
AUDIO_DIR = ROOT / "outputs" / "audio"
MUSIC = ROOT / "outputs" / "music" / "final_music.wav"
SUBTITLES = ROOT / "outputs" / "subtitles" / "english.srt"

TEMP_DIR = ROOT / "outputs" / "assembly_temp"
FINAL_DIR = ROOT / "outputs" / "final"

FINAL_VIDEO = FINAL_DIR / "father_care_16x9.mp4"


def load_storyboard():
    with STORYBOARD.open("r", encoding="utf-8") as f:
        return json.load(f)


def run(command):
    print("\nRunning FFmpeg...")
    subprocess.run(command, check=True)


def main():

    storyboard = load_storyboard()

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    story_shots = [
        shot for shot in storyboard["shots"]
        if shot["id"] != "end_card"
    ]

    # ------------------------------------------------
    # STEP 1: Create list of visual clips
    # ------------------------------------------------

    video_list = TEMP_DIR / "video_list.txt"

    video_list.write_text(
        "\n".join(
            f"file '{(SHOTS_DIR / f'{shot['id']}.mp4').as_posix()}'"
            for shot in story_shots
        ),
        encoding="utf-8"
    )

    story_video = TEMP_DIR / "story_video.mp4"

    run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(video_list),
        "-c", "copy",
        str(story_video)
    ])

    # ------------------------------------------------
    # STEP 2: Build narration timeline
    # ------------------------------------------------

    audio_inputs = []
    filters = []
    labels = []

    for i, shot in enumerate(story_shots):

        shot_id = shot["id"]
        duration = float(shot["duration_seconds"])

        audio_file = AUDIO_DIR / f"{shot_id}.wav"

        audio_inputs.extend([
            "-i",
            str(audio_file)
        ])

        label = f"a{i}"

        filters.append(
            f"[{i}:a]"
            f"aformat=sample_rates=44100:channel_layouts=mono,"
            f"apad,"
            f"atrim=duration={duration}"
            f"[{label}]"
        )

        labels.append(f"[{label}]")

    filters.append(
        "".join(labels)
        + f"concat=n={len(labels)}:v=0:a=1[narration]"
    )

    narration_file = TEMP_DIR / "narration.wav"

    run([
        "ffmpeg",
        "-y",
        *audio_inputs,
        "-filter_complex",
        ";".join(filters),
        "-map", "[narration]",
        "-ar", "44100",
        str(narration_file)
    ])

    # ------------------------------------------------
    # STEP 3: Mix narration + music
    #
    # Music stays intentionally quiet.
    # ------------------------------------------------

    mixed_audio = TEMP_DIR / "mixed_audio.wav"

    run([
        "ffmpeg",
        "-y",

        "-i", str(narration_file),
        "-i", str(MUSIC),

        "-filter_complex",
        (
            "[0:a]volume=1.0[n];"
            "[1:a]volume=0.14[m];"
            "[n][m]amix=inputs=2:"
            "duration=first:"
            "dropout_transition=2[a]"
        ),

        "-map", "[a]",
        "-ar", "44100",
        str(mixed_audio)
    ])

    # ------------------------------------------------
    # STEP 4: Add narration/music + English subtitles
    # ------------------------------------------------

    subtitled_story = TEMP_DIR / "story_subtitled.mp4"

    # Windows FFmpeg subtitle paths behave better when
    # using a relative path from the project root.
    subtitle_filter = (
        "subtitles='outputs/subtitles/english.srt':"
        "force_style='"
        "FontName=Arial,"
        "FontSize=22,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=0,"
        "Alignment=2,"
        "MarginV=45"
        "'"
    )

    run([
        "ffmpeg",
        "-y",

        "-i", str(story_video),
        "-i", str(mixed_audio),

        "-vf", subtitle_filter,

        "-map", "0:v",
        "-map", "1:a",

        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        "-shortest",

        str(subtitled_story)
    ])

    # ------------------------------------------------
    # STEP 5: Create 4-second visual-only AI disclosure
    # ------------------------------------------------

    disclosure = TEMP_DIR / "disclosure.mp4"

    disclosure_text = (
        "This film was created with the assistance "
        "of generative AI."
    )

    run([
        "ffmpeg",
        "-y",

        "-f", "lavfi",
        "-i", "color=c=black:s=1920x1080:r=30:d=4",

        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",

"-vf",
(
    "drawtext="
    "fontfile='C\\:/Windows/Fonts/arial.ttf':"
    f"text='{disclosure_text}':"
    "fontcolor=white:"
    "fontsize=42:"
    "x=(w-text_w)/2:"
    "y=(h-text_h)/2"
),


        "-t", "4",

        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        str(disclosure)
    ])

    # ------------------------------------------------
    # STEP 6: Concatenate story + disclosure
    # ------------------------------------------------

    final_list = TEMP_DIR / "final_list.txt"

    final_list.write_text(
        "\n".join([
            f"file '{subtitled_story.as_posix()}'",
            f"file '{disclosure.as_posix()}'"
        ]),
        encoding="utf-8"
    )

    run([
        "ffmpeg",
        "-y",

        "-f", "concat",
        "-safe", "0",
        "-i", str(final_list),

        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        str(FINAL_VIDEO)
    ])

    print("\n================================")
    print("FINAL 16:9 FILM CREATED")
    print("================================")
    print(FINAL_VIDEO)


if __name__ == "__main__":
    main()