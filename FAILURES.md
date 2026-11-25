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