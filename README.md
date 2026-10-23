<!-- register: technical -->

# LDTMP

LDTMP (Layered Depth Tension Modulation Protocol) paces how deep a conversation between a person and an AI interviewer goes. It defines six layers, from an icebreaker down to the most personal material and back up to a forward-looking close. Deterministic rules move the session between layers based on measured engagement, and a safety gate vetoes any descent when the person shows signs of fatigue or withdrawal. Deterministic rules set the depth, and the language model writes one question at a time inside the constraints of the current layer.

The protocol came out of a production voice app that interviews people about their memories. It applies equally well to coaching, interview practice, user research and onboarding conversations.

## Files

| File | Contents |
|---|---|
| [`LDTMP.md`](LDTMP.md) | The specification, with three worked examples that double as test vectors. |
| [`ldtmp.config.json`](ldtmp.config.json) | Every constant in the specification, in machine-readable form. |
| [`CITATION.cff`](CITATION.cff) | Citation metadata. |
| [`LICENSE`](LICENSE) | Creative Commons Attribution 4.0 International. |

An agent implementing LDTMP should read `LDTMP.md` for the rules and load `ldtmp.config.json` for the numbers.

## License

Copyright (c) 2026 Alexander Milovidov. LDTMP is released under CC BY 4.0. Anyone may use, adapt and redistribute it, and commercial use is allowed. Every reuse must credit the author, for example with this line:

> Based on LDTMP (Layered Depth Tension Modulation Protocol) by Alexander Milovidov, https://github.com/amilovidov/ldtmp, CC BY 4.0.

LDTMP is a conversation-design protocol and has no clinical standing. The scope section of the specification explains its limits.
