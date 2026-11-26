For Me, My Father Was Care
An AI-assisted short-film production pipeline built for the 10 Academy Week 0 Film Production Challenge.

The film is based on personal childhood memories of my father and the small acts of care that remained with me as I grew older.

The final film uses:

Amharic narration
English subtitles
AI-generated / AI-assisted visuals
slow cinematic image motion
an original Ethiopian-jazz-inspired instrumental score
a visible generative-AI disclosure
The project is designed as a reproducible pipeline rather than a collection of manually edited media files.

Film
Title: For Me, My Father Was Care

Language: Amharic narration

Subtitles: English

Length: approximately 89 seconds including the AI disclosure

Primary format: 16:9

Additional target format: 9:16

Final 16:9 output:

outputs/final/father_care_16x9.mp4

Story
The film is based on childhood memories of my father and the ways he cared for me.

The story moves through small memories including:

going with him to his nearby office;
sitting beside him while he worked;
waiting for tea and donuts;
receiving calm guidance when I struggled at school;
the physical care he gave me at home;
missing him when he travelled for fieldwork; and
the happiness I felt when he returned.
The final reflection connects these memories to a broader idea of fatherhood and care.

The story is personal, but the visual characters are fictionalized representations rather than replicas of real people.

Pipeline
storyboard.json is the central contract for the film.

It contains:

shot IDs;
shot durations;
Amharic narration;
English subtitles;
visual prompts;
motion prompts;
music direction; and
AI-disclosure information.
The production pipeline follows this structure:

storyboard.json
        |
        v
JSON Schema Validation
        |
        +----------------------------+
        |                            |
        v                            v
Amharic Narration                Keyframes
Gemini TTS                      Image generation
        |                            |
        v                            v
outputs/audio/              outputs/keyframes/
        |                            |
        |                            v
        |                         shots.py
        |                            |
        |                      FFmpeg motion
        |                            |
        |                            v
        |                      outputs/shots/
        |                            |
        +-------------+--------------+
                      |
                      v
                 subtitles.py
                      |
                      v
           outputs/subtitles/
                      |
                 Music track
                      |
                      v
                 assemble.py
                      |
                      v
        narration + visuals + music
            + English subtitles
                      |
                      v
             AI disclosure card
                      |
                      v
              Final film output

One-command pipeline
After the required generated/cached production assets are available, the complete deterministic production pipeline can be run with:Final film:
C:\Personal\TRP2\Week 0\week0-film-production\outputs\final\father_care_16x9.mp4