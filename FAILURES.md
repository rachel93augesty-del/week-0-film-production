Failure 1: Narration API request format

Problem:
The first Gemini TTS test for shot_01 failed with HTTP 400 INVALID_ARGUMENT.

Error:
Unknown name "speechConfig" at generation_config.

Cause:
The narration script used a TTS configuration shape that did not match the API endpoint being called.

Action:
Checked the current Gemini TTS documentation and migrated the narration request to the recommended Interactions API.

Result:
Pending retest.

Failure 2: Shot 2 narration regeneration stalled
Problem
During review of the Amharic narration, I noticed that the word "ጭቅጭቅ" in Shot 2 did not sound as natural as I wanted. The TTS pronunciation was heavier than the way I would normally say the word in conversational Amharic.

First attempt
I tried regenerating Shot 2 with the original narration using:

python pipeline/narration.py --shot shot_02 --force

The generation remained pending and did not return a completed audio file.

Second attempt
I changed the wording from "ጭቅጭቅ" to a more conversational alternative using "እወተውተው" and regenerated Shot 2.

The generation again stalled without completing.

Additional test
I simplified the wording further to check whether the specific Amharic expression was causing the problem.

The Shot 2 generation still did not complete, while regeneration of other shots such as Shot 5 and Shot 6 completed successfully.

Conclusion
Because several different versions of the Shot 2 text produced the same stalled behavior, I concluded that the issue was unlikely to be caused only by the word "ጭቅጭቅ".

The rest of the narration pipeline was functioning, so this appeared to be an isolated or intermittent model/API generation problem.

Workaround
I retained the previously generated Shot 2 audio, which was usable even though the pronunciation was not ideal.

I decided not to allow a minor pronunciation improvement to block the rest of the production pipeline.

Status
Workaround accepted. Production continued using the earlier Shot 2 audio.

Failure 3: Cloudflare Workers AI daily allocation exhausted

Plan
Free Workers AI allocation.

Observed Usage Constraint
The daily free allocation of 10,000 Neurons was exhausted during keyframe experimentation and production.

Before reaching the limit, I was able to generate:

7 usable production keyframes; and
2 additional trial/reference-consistency generations.
After these generations, Cloudflare returned an HTTP 429 response indicating that the daily free allocation had been exhausted.

Effect on Production
The free allowance was sufficient for the initial model experiments and production of Shots 1–7, but it was exhausted before Shots 8–11 could be generated.

As a result, 4 production keyframes remained incomplete.

Production Decision
I stopped further Cloudflare API calls after receiving the quota error, rather than repeatedly submitting requests that could not succeed.

The remaining keyframes, Shots 8–11, will be generated after the daily free allocation resets.

At the time the quota was reached, the next reset was approximately 6 hours away, so I continued working on pipeline components that did not depend on additional image generation.

Cost and Resource Learning
The main constraint was not a direct monetary cost, but the limited daily compute budget.

In this run, the 10,000-Neuron allowance supported approximately 9 image-generation calls in total:

7 final production images;
2 experimental/trial generations.
This showed that experimentation and final production compete for the same compute allowance.

For a future run, I would reserve part of the available generation budget specifically for final production before using the remaining capacity for model and prompt experiments.