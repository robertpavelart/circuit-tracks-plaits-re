> Historical experiment scope, not the current global project stop point. [Current state](../../../docs/CURRENT_STATUS.md).

# Offline legal timing domain

Analysis-only layer over the unchanged 442P REGOPT standalone renderer. No new
oscillator arithmetic, assembler/core edits, stock image execution, hardware or
firmware integration. Resources and both baseline implementations stay frozen.

domain.py projects the exact integer ramp/phase/high/PW transition onto every
data-dependent branch and imports the existing instruction timing rules.
search.py uses legal histories from reset and keeps every improved maximum.
verify.py runs the unchanged existing executable twice and compares independent
oracle samples, all7 state words, fullPC traces and calculated cycles. The
executable's immutable output guard requires new phase20a-regopt children; their
evidence is copied to the requested fresh phase20a-bound verification directory.
prove.py qualifies against existing traces and exhausts a finite event/cooldown
relaxation; algebraic domain lemmas are in the report. export.py consumes frozen
proof-final/verified-final evidence and checks immutable source/artifact guards.

The final13379 bound includes12 boundary cycles. Reachable13335 is DSP-tested;
32 further event-ordering cycles are unresolved. No attained-bound or exhaustive
full24-bit-state claim. Deferred-wrap exception has two k1 ratios and11603 bound.
Use fresh output directories; every script refuses overwrites.

Report and reproducible commands:notes/plaits-reachable-timing-bound.md.
Canonical outputs:builds/phase20a-bound/final/.
