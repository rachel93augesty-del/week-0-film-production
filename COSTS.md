Cloudflare Workers AI
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