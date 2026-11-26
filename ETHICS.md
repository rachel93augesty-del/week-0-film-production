Ethics
Story and Representation
This film is based on my real childhood memories and my relationship with my father.

The events described in the narration are personal memories, but the visual characters in the film are fictionalized representations.

The film does not attempt to reconstruct the exact appearance of my father or my childhood appearance.

This separation between real memories and fictionalized visuals was an intentional design and ethics decision.

Likeness and Consent
The film does not use an AI-generated replica of my father's real face.

I did not upload or use my father's real photograph as an identity reference for generating the recurring character.

The adult character is instead a fictionalized representation based on general characteristics relevant to the memories.

The child character is also fictionalized and does not attempt to reconstruct an identifiable real child's face.

Because the production avoids reproducing identifiable real-person facial likenesses, the film does not present its generated characters as synthetic replicas of real family members.

Voice and Audio Consent
The film does not clone the voice of my father, myself, or another identifiable person.

The Amharic narration was generated using a synthetic Gemini text-to-speech voice.

The narration communicates my own written personal story, but the voice itself is not presented as belonging to a real person.

Human Review
AI-generated outputs were reviewed by me before being accepted into the film.

Human review included:

Amharic pronunciation;
natural phrasing;
emphasis;
speaking pace;
transition timing;
character consistency;
visual relevance;
image quality; and
final film coherence.
Some generated narration was regenerated after human review.

Some visual generations were rejected because the recurring characters drifted too far from the approved fictional reference.

A usable earlier narration output was retained for one shot when repeated attempts to improve a minor pronunciation issue failed. That limitation is documented in FAILURES.md.

The film was also reviewed by three audience participants across the radio-cut and near-final stages.

AI Disclosure and Labelling
The final film explicitly discloses the use of generative AI.

The final disclosure shown on screen is:

"This film was created with the assistance of generative AI."

The disclosure appears as written English text at the end of the film.

It is intentionally not narrated.

An experimental AI-disclosure narration file was generated earlier in development, but it is excluded from the final assembly.

AI use will also be disclosed in the repository documentation and in the public post/submission material.

Where the publishing platform provides an AI-content label, that label will be enabled.

Models and Tools
Gemini Text-to-Speech
Purpose: Generate Amharic narration from the narration text stored in storyboard.json.

The model uses a synthetic voice. No identifiable person's voice was cloned.

Cloudflare Workers AI / FLUX
Purpose: Generate and evaluate film keyframes.

FLUX.1 Schnell, FLUX.2 Klein and FLUX.2 Dev were evaluated during experimentation.

Generated images were reviewed by a human before being accepted.

Microsoft Copilot
Purpose: Assist with development, troubleshooting, documentation, visual design and fallback visual generation during provider limitations.

Any AI-generated visual incorporated through this fallback is treated as AI-generated content under the same disclosure policy as the other generative outputs.

FFmpeg and FFprobe
Purpose: Deterministic local media processing.

FFmpeg was used for:

audio assembly;
shot motion;
music mixing;
subtitle rendering;
disclosure-card rendering; and
final video encoding.
FFprobe was used to inspect media properties and timing.

These tools processed existing media rather than generating story content.

Pillow
Purpose: Local image format handling during image-generation experiments.

Pillow was used for image decoding/conversion rather than semantic image generation.

Music and Copyright
The film does not use a copied commercial song.

The final soundtrack was created specifically for this project.

The chosen direction is a slow, calm, Ethiopian-jazz-inspired instrumental designed to support the Amharic narration.

The soundtrack is not intended to reproduce a specific copyrighted song or recording.

Licensing and Output-Use Record
Model and tool usage is documented in the repository so that the origin of generated and processed assets can be inspected.

runs.jsonl records the provider/model associated with model calls where applicable.

Provider usage and output conditions should be interpreted according to the applicable terms of service and model licence for the provider/model used at the time of generation.

The project does not claim ownership of third-party model software.

Locally used open-source software, including FFmpeg and Pillow, remains subject to its respective software licence.

No third-party commercial music, stock footage or copyrighted film material was intentionally incorporated into the final film.

Privacy and Secrets
API credentials are stored locally in .env.

.env is excluded from Git through .gitignore.

The repository includes .env.example containing placeholder variable names only.

Real API keys and tokens are not intentionally published in the repository.

Provider Transparency
The production tested multiple generative providers because quality and resource availability varied during development.

Provider failures and fallback decisions are documented rather than hidden.

These included:

Cloudflare Workers AI quota limits;
Gemini image-generation quota restrictions; and
fal.ai account-balance restrictions.
The downstream pipeline was designed around expected media artifacts rather than a single provider, allowing production to continue when a provider became unavailable.

Ethical Trade-Off: Character Consistency vs. Exact Replication
Reference-aware image models were tested in an attempt to improve character consistency.

Even with reference conditioning, the generated characters did not perfectly reproduce the approved fictional reference.

I decided not to continue pursuing exact facial replication.

This was appropriate for the project because the purpose of the visuals was to represent personal memories, not to create synthetic replicas of real family members.

The narration carries the factual and personal relationship to the memories, while the visuals remain clearly fictionalized representations.

Final Ethics Position
The project uses generative AI as a production tool while keeping the personal story under human control.

The main safeguards are:

no cloning of a real person's voice;
no attempt to reproduce my father's exact face;
fictionalized child representation;
human review of generated narration and visuals;
explicit written AI disclosure in the final film;
public/submission labelling of AI assistance;
no copyrighted commercial soundtrack; and
secure handling of API credentials.