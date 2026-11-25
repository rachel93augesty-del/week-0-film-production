import wave
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = PROJECT_ROOT / "outputs" / "audio"


def get_wav_duration(file_path):
    with wave.open(str(file_path), "rb") as wav:
        frames = wav.getnframes()
        frame_rate = wav.getframerate()

        return frames / float(frame_rate)


def main():

    audio_files = sorted(AUDIO_DIR.glob("*.wav"))

    if not audio_files:
        print("No WAV files found.")
        return

    total_duration = 0

    print("\nNarration durations\n")
    print(f"{'File':<20} {'Duration':>10}")
    print("-" * 32)

    for audio_file in audio_files:

        duration = get_wav_duration(audio_file)
        total_duration += duration

        print(
            f"{audio_file.name:<20} "
            f"{duration:>8.2f} sec"
        )

    print("-" * 32)
    print(
        f"{'TOTAL':<20} "
        f"{total_duration:>8.2f} sec"
    )


if __name__ == "__main__":
    main()