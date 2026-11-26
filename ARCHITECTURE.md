Architecture
Overview
The project uses a storyboard-driven multimodal pipeline.

storyboard.json acts as the central contract connecting narration, visual generation, shot timing, subtitles, music and final assembly.

The pipeline was designed so that individual stages can be rerun without rebuilding the complete film.

Pipeline
storyboard.json | v JSON Schema Validation | +-----------------------------+ | | v v Narration Keyframes Gemini TTS Image models | | v v outputs/audio/ outputs/keyframes/ | | | v | shots.py | | | FFmpeg motion | | | v | outputs/shots/ | | +--------------+--------------+ | v subtitles.py | v outputs/subtitles/ | + | Music track | v assemble.py | v narration + visuals + music + English subtitles | v visual AI disclosure | v final 16:9 film output

Storyboard Contract
Every production shot contains structured fields including:

shot ID;
duration;
Amharic narration;
English subtitle;
visual prompt;
motion direction; and
music mood.
This allows each pipeline stage to consume the same source of truth instead of duplicating prompts or timing information across scripts.

Validation
pipeline/validate_storyboard.py validates storyboard.json against the JSON Schema before downstream production.

Additional checks include:

unique shot IDs;
total film duration;
required aspect ratios; and
presence of the AI disclosure.
Narration
pipeline/narration.py reads narration_amharic for an individual shot and generates Amharic speech using Gemini TTS.

Generated narration is cached in:

outputs/audio/

Existing audio is reused unless regeneration is explicitly requested.

This allowed individual narration shots to be revised without regenerating the complete voice track.

Keyframes
The visual pipeline initially used Cloudflare Workers AI.

Several FLUX variants were evaluated for character consistency.

Provider limitations later required fallback approaches for some production keyframes.

Regardless of provider, downstream stages depend only on the artifact contract:

outputs/keyframes/shot_XX.jpg

This keeps later stages independent from the image-generation provider.

Motion
pipeline/shots.py converts keyframes into timed 16:9 video clips using FFmpeg pan and zoom motion.

Motion varies by story moment rather than applying one identical effect to every frame.

The generated clips are stored in:

outputs/shots/

Music
The film uses a quiet Ethiopian-jazz-inspired instrumental score designed to remain underneath the narration.

The score becomes sparser during the separation memory and lifts gently during the reunion and closing sections.

Subtitles
pipeline/subtitles.py reads subtitle_english and shot durations from the storyboard and generates:

outputs/subtitles/english.srt

This keeps English subtitle timing connected to the same storyboard timeline used by the visuals and narration.

Assembly
pipeline/assemble.py uses FFmpeg to:

concatenate the 11 visual shot clips;
recreate the narration timeline;
mix narration with the instrumental score;
burn in English subtitles;
create the final visual AI-disclosure card; and
export the final 16:9 film.
The AI disclosure is visual English text only. The previously generated end-card narration is intentionally excluded from final assembly.

Caching
Generated media files act as a simple cache.

Existing narration, keyframes and shot clips are reused unless intentional regeneration is requested.

This reduces unnecessary model calls, latency and cost.

Logging
runs.jsonl stores one record for model calls including:

stage;
provider/model;
shot ID;
success/failure status;
generation latency; and
output path where available.
Failure Handling
The pipeline encountered several real production failures, including:

Gemini TTS request-format mismatch;
Gemini API-version/model-routing issue;
stalled targeted TTS regeneration;
Cloudflare authentication/request-schema problems;
reference-image character drift;
Cloudflare Workers AI quota exhaustion;
Gemini image-generation quota restrictions; and
fal.ai account-balance limitations.
Failures and workarounds are documented in FAILURES.md.

A key design principle that emerged from these failures was provider independence: downstream stages operate on expected output artifacts rather than depending directly on a specific AI provider.

Secrets
API credentials are stored in .env, which is excluded from Git.

.env.example documents required environment-variable names without containing real credentials.

Final Output
Primary final artifact:

outputs/final/father_care_16x9.mp4