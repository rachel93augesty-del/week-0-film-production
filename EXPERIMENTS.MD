Experiment 1: Amharic narration quality

Hypothesis: Gemini TTS can produce sufficiently natural Amharic narration for a personal and emotional childhood story.

Test: Generated Shot 01 using the Kore voice with a warm, gentle and reflective narration style.

Result: The generated Amharic sounded surprisingly natural, with clear pronunciation and high audio quality and i was amused with the resul and this is something i should keep working on.

Decision: Keep the current voice and narration style for the remaining shots.

Experiment 2: Radio_Cut Pacing
Experiment 2: Improving the transition after the tea-and-donut memory
Hypothesis
Adding a pause after the tea-and-donut memory will make the transition to the school-guidance section feel more natural.

Observation
In the first radio cut, Shot 5 started almost immediately after Shot 4. The emotional transition felt too abrupt.

First change
Added a 1.5-second intentional pause after Shot 4.

Result
The pipeline correctly rejected the change because Shot 4 narration was 7.77 seconds. Narration plus a 1.5-second pause required 9.27 seconds, while Shot 4 was allocated only 8 seconds.

Second change
Rebalanced the timeline instead of changing or speeding up the narration:

Increased Shot 4 duration.
Reduced unnecessary pause elsewhere in the film.
Adjusted the intentional pause to fit the available timeline.
Kept the complete film within the 90-second limit.
Result
Pending final listening comparison.

Decision
Keep the revised timing if the new radio cut produces a more natural transition.

Experiment 3: Improving natural Amharic pronunciation, wording and emphasis
Hypothesis
Targeted human review of the AI narration can make the output sound more like natural conversational Amharic while preserving the emotional meaning of the story.

Observations
After listening to the generated narration, I identified several places where the AI voice did not fully match natural Amharic speech:

In Shot 2, "ጭቅጭቅ" was pronounced more strongly than I would naturally say it.
In Shot 5, "ይረዳኛል" was delivered too lightly. I wanted slightly stronger emphasis because my father's support is important to the meaning.
The final sentence in Shot 5 did not sound as natural as the way I would normally express the idea.
"ጮክ" needed to sound naturally as "chok".
Changes
Reviewed the wording and pronunciation of "ጭቅጭቅ" in Shot 2.

In Shot 5, kept emphasis on:

"ይረዳኛል"

and revised the closing sentence to:

"ጮክ ብሎ ግን አናግሮኝ አያውቅም።"
In Shot 2, changed "ጭቅጭቅ" to "እወተውተው" because i dont get the actual pronounciation by AI. 

Method
Regenerate only the affected shots:

python pipeline/narration.py --shot shot_02 --force

python pipeline/narration.py --shot shot_05 --force

python pipeline/narration.py --shot shot_06 --force

Then rebuild the radio cut:

python pipeline/radio_cut.py

Result
Pending comparison.

Decision
Keep the regenerated versions only if they sound more natural while preserving the intended meaning and emotional tone.