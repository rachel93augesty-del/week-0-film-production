import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

STORYBOARD_PATH = ROOT / "storyboard.json"
OUTPUT_DIR = ROOT / "outputs" / "subtitles"
OUTPUT_FILE = OUTPUT_DIR / "english.srt"


def load_storyboard():
    with STORYBOARD_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def srt_time(seconds):
    milliseconds = round(seconds * 1000)

    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000

    minutes = milliseconds // 60_000
    milliseconds %= 60_000

    secs = milliseconds // 1000
    milliseconds %= 1000

    return (
        f"{hours:02}:"
        f"{minutes:02}:"
        f"{secs:02},"
        f"{milliseconds:03}"
    )


def main():

    storyboard = load_storyboard()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    current_time = 0.0
    subtitle_number = 1
    blocks = []

    for shot in storyboard["shots"]:

        shot_id = shot["id"]
        duration = float(shot["duration_seconds"])

        start = current_time
        end = current_time + duration

        # The disclosure is visual text only.
        if shot_id != "end_card":

            subtitle = (
                shot.get("subtitle_english", "")
                .strip()
            )

            if subtitle:

                blocks.append(
                    f"{subtitle_number}\n"
                    f"{srt_time(start)} --> "
                    f"{srt_time(end)}\n"
                    f"{subtitle}\n"
                )

                subtitle_number += 1

        current_time = end

    OUTPUT_FILE.write_text(
        "\n".join(blocks),
        encoding="utf-8"
    )

    print("SUBTITLES COMPLETE")
    print(f"Saved: {OUTPUT_FILE}")
    print(
        f"Timeline duration: "
        f"{current_time:.2f}s"
    )
    print(
        f"Subtitle entries: "
        f"{subtitle_number - 1}"
    )


if __name__ == "__main__":
    main()