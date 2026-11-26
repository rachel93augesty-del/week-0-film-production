Costs and Measurements
Overview
The project primarily used free API allocations and local processing.

The largest resource constraint was not direct monetary spending, but the limited compute quota available for generative model calls.

Measurements were recorded during narration generation, image generation, audio timing and final production.

Production Measurements
Measurement	Observed Result
Final film duration	89 seconds
Story duration before AI disclosure	85 seconds
AI disclosure duration	4 seconds
Approximate generated Amharic narration duration	75 seconds
Number of story shots	11
Final keyframes required	11
Final motion clips produced	11
Gemini TTS Shot 1 generation latency	9.08 seconds
FLUX.1 Schnell Shot 1 generation latency	5.43 seconds
FLUX.2 Dev Shot 1 generation latency	49.71 seconds
Cloudflare Workers AI free daily allocation	10,000 Neurons
Production keyframes generated before quota exhaustion	7
Image trial/reference generations before quota exhaustion	2
Keyframes blocked after quota exhaustion	4
Narration Timing
The Amharic narration was measured from the generated WAV files rather than relying only on estimated speaking time.

The narration totalled approximately 75 seconds.

The complete story timeline was 85 seconds, leaving approximately 10 seconds for intentional pauses, transitions and music before the 4-second AI disclosure.

This allowed the narration to remain natural instead of being artificially sped up to fill the complete film duration.

Individual WAV durations were also compared with the planned duration of each storyboard shot.

This exposed timing conflicts during production.

For example, the tea-and-donut narration measured approximately 7.77 seconds. The original visual allocation for the shot was 8 seconds, which left almost no space for the intentional pause identified during the radio-cut review.

The visual timeline was therefore rebalanced rather than changing the natural narration speed.

Gemini TTS
Gemini text-to-speech was used for the Amharic narration.

One measured generation:

Shot 1 generation latency: 9.08 seconds
The generated narration was reviewed for:

pronunciation;
pacing;
emphasis;
natural Amharic delivery; and
emotional suitability.
Only affected narration clips were regenerated after review rather than regenerating the complete narration set.

This reduced unnecessary API calls.

Cloudflare Workers AI
Plan
Free Workers AI allocation.

Observed Usage Constraint
The daily free allocation of 10,000 Neurons was exhausted during keyframe experimentation and production.

Before reaching the limit, I was able to generate:

7 usable production keyframes; and
2 trial/reference-consistency generations.
After these generations, Cloudflare returned HTTP 429 indicating that the daily free allocation had been exhausted.

Measured Image Latency
Examples recorded during model testing included:

FLUX.1 Schnell Shot 1: 5.43 seconds
FLUX.2 Dev Shot 1: 49.71 seconds
The difference demonstrated that higher-quality/reference-aware generation also introduced materially higher latency.

Effect on Production
The allocation supported keyframe experimentation and production of Shots 1–7 but was exhausted before Shots 8–11 could be generated.

As a result:

7 production images were completed through the main provider
4 production keyframes were initially blocked
The remaining images were completed through the project's fallback production strategy so that the provider quota did not prevent completion of the film.

Production Decision
I stopped repeatedly submitting Cloudflare requests once the API confirmed that the allocation was exhausted.

At the time, I initially expected the quota to reset approximately 6 hours later and continued working on pipeline components that did not depend on additional image generation.

When the API remained unavailable after the expected reset window, I moved to fallback options rather than allowing image generation to block the complete production pipeline.

Alternative Provider Tests
Alternative image-provider routes were evaluated after the Cloudflare quota was exhausted.

Gemini Image Generation
The request successfully reached the Gemini image model but returned HTTP 429 RESOURCE_EXHAUSTED.

The project reported a free-tier request limit of 0 for the requested image model and a retry period that exceeded the remaining production window.

fal.ai
The API key successfully reached fal.ai, but the provider returned HTTP 403 indicating that the account balance was exhausted.

These tests confirmed that provider switching itself can introduce additional financial or quota constraints.

Local Processing
FFmpeg handled the deterministic production stages locally, including:

radio-cut assembly;
narration alignment;
image-to-motion conversion;
narration and music mixing;
subtitle rendering;
AI-disclosure rendering; and
H.264/AAC final encoding.
The final story video before disclosure measured 85 seconds.

A 4-second text-only AI-disclosure card was appended, producing the complete 89-second film.

Because these stages ran locally, they did not consume additional generative-model quota.

Music
The final soundtrack was created specifically for this film.

The selected direction was a slow, calm, Ethiopian-jazz-inspired instrumental rather than a sad cinematic score.

The final music track was approximately 89 seconds, matching the complete production timeline.

During assembly, the music level was reduced beneath the Amharic narration so that the voice remained the primary audio element.

Direct Monetary Cost
The project was intentionally developed primarily using available free model allocations and local processing.

The main measured cost constraint was therefore compute availability rather than a significant direct monetary charge.

No third-party commercial music licence was purchased because the instrumental score was created specifically for this project.

Cost and Resource Learning
The 10,000-Neuron Cloudflare allocation supported approximately 9 image-generation calls during this production run:

7 production images;
2 experimental/reference-comparison generations.
This should not be interpreted as a universal conversion of 10,000 Neurons into exactly 9 images because different models and generation configurations consume different amounts of compute.

It represents the observed output of this specific production run.

The experience showed that experimentation and final production compete for the same finite model budget.

For a future run, I would:

estimate the number of required final assets before experimentation;
reserve part of the generation allowance specifically for final production;
place a strict cap on experimental generations;
monitor cumulative provider usage throughout the run;
compare paid API cost against the engineering time spent working around free-tier limits; and
keep downstream pipeline stages provider-independent so production can continue when one provider becomes unavailable. 