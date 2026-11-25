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

Experiment 4: Image Generation_Character consistency using text-only FLUX.1 Schnell

Hypothesis
Using the same locked father and daughter character descriptions together with the shot-specific visual prompt would allow FLUX.1 Schnell to produce characters sufficiently close to the approved father-daughter visual reference.

Baseline
Before generating the film keyframes, I created and approved a father-daughter reference image and the reference established the following intended results:

approximate ages of the two characters;
facial appearance and general proportions;
father's short haircut and moustache;
daughter's hairstyle and age;
clothing;
early-2000s visual period; and
warm photorealistic cinematic style.
This approved reference became the visual baseline for evaluating subsequent keyframes.

Test
I generated Shot 1 through the Python keyframe pipeline using:

Model: FLUX.1 Schnell
Provider: Cloudflare Workers AI
Steps: 4
Input: Shot 1 visual prompt from storyboard.json
Locked father character description
Locked daughter character description
Early-2000s Ethiopian visual-style constraints
Generation completed successfully in 5.43 seconds.

Result
The generated Shot 1 was technically successful and broadly followed the requested scene and style, but the recurring characters were too far from what i have approved visual reference.

The approved reference was considerably closer to the intended character appearance and therefore remained the stronger baseline.

Text descriptions alone were not sufficient to maintain the visual identity I wanted for the film.

Decision
I rejected the Shot 1 output as the final keyframe.

I decided not to generate Shots 2–11 using the same text-only approach, because doing so would likely create substantial character drift and waste additional model calls.

The next experiment will use the approved character reference as an image input with a reference-aware image-generation method.

Learning
A detailed prompt can describe character attributes, but description alone does not guarantee identity consistency across generated images.

For a film with recurring characters, reference-image conditioning is more appropriate than relying only on repeated text descriptions.

Experiment 5: Reference-conditioned character consistency with FLUX.2 Klein 9B

Hypothesis
Providing the approved father-daughter reference image directly to a reference-aware image model would preserve the recurring character identities substantially better than the earlier text-only FLUX.1 Schnell approach.

Test
I regenerated Shot 1 using FLUX.2 Klein 9B through Cloudflare Workers AI.

The generation request included:

the approved father-daughter reference image;
the Shot 1 visual prompt from storyboard.json;
locked father identity instructions;
locked daughter identity instructions; and
the established early-2000s cinematic style.
Result
The output improved substantially in photorealism, lighting, environment and overall cinematic quality. However, the two generated characters still differed significantly from the approved visual baseline.
The adult character did not preserve the approved facial identity and age characteristics closely enough.
The child character also showed noticeable identity drift despite following some requested characteristics such as the general hairstyle and simple period clothing.

As a result, the image was visually stronger but still not sufficiently consistent for use as the recurring-character baseline for the film.

Decision
Reject this Shot 1 output as the final keyframe.

Do not generate the remaining ten shots using the same configuration.

Learning
Direct reference conditioning improved overall visual quality but did not fully solve recurring-character consistency.

A possible reason is that a single reference image contains both recurring characters, which may make it difficult for the model to associate each identity independently with the corresponding character instructions.

The next test should separate the recurring character references rather than relying on one combined two-character image.


Experiment 6: Stronger reference preservation with FLUX.2 Dev
Hypothesis
FLUX.2 Dev with stronger identity-preservation instructions would reproduce the approved recurring characters more closely than the previous reference-conditioned FLUX.2 Klein 9B result.

Test
Shot 1 was regenerated using FLUX.2 Dev with the same approved father-daughter reference image and substantially stronger instructions to preserve facial identity, apparent age, hairstyle, moustache, proportions and recognizable appearance.

Result
The output improved compared with earlier attempts and produced a coherent, natural-looking cinematic scene.

However, the characters still did not reproduce the approved reference closely enough to treat the reference as an exact identity anchor.

Although some requested characteristics were preserved, the facial identity and overall appearance still changed during generation.

Decision
I stopped pursuing exact reference replication.

The approved reference will instead be used as a visual design guide for approximate age, hairstyle, clothing, character relationship, period and cinematic style.

For the remaining keyframes, the goal will be reasonable visual continuity rather than exact identity replication.

Learning
Reference-aware generative image models can improve visual continuity, but providing a reference does not guarantee exact identity preservation when pose, environment and composition are also being changed.

Given the project deadline, continuing to regenerate a single frame for perfect identity fidelity would have reduced the probability of completing the full film.