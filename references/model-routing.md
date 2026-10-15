# Codex model, effort, and usage routing

Research checked 2026-09-30 (Asia/Shanghai). Dated evidence and billing are in [benchmark-evidence.md](benchmark-evidence.md). These starting choices are judgments, not measured success rates for the user's projects.

Routing policy updated 2026-10-10: preserve full completion, required quality, and end-to-end completion efficiency, then minimize expected comprehensive task cost: each model's usage weighted by applicable rates, plus billable services and rework. Raw token count is a secondary metric, not the cost objective. This does not refresh the September 30 benchmark snapshot; the credit rate table was separately rechecked on October 4 in [benchmark-evidence.md](benchmark-evidence.md).

## Actual controls take precedence

The user confirms their Codex picker has **no Max option**. Never recommend Max, reconstruct it from API settings, or suggest Fast/Ultrafast secretly selects it. Only an explicit later user update to their available controls can revise this boundary. Backend catalogs and public docs do not override it.

- **Model:** distinguish GPT-6.1 Sol from old GPT-6 Sol.
- **Reasoning strength:** Low / Medium / High / X-High, restricted to observed available settings. Use Light/Extra High instead if those are the actual UI labels.
- **GPT-6 Luna:** X-High only, preserving this user's preference. This is a preference, not a claim about the product's maximum.
- **Execution arrangement:** single agent or Sol/Astra host with Luna X-High workers. Explicit ordinary Codex delegation does not require Ultra; use [hybrid-delegation.md](hybrid-delegation.md) for complex delegable work.
- **Ultra:** separate availability-dependent delegation mode, not a prerequisite for explicitly requested subagents. Do not rename it Max or Ultrafast.
- **Speed:** Standard / Fast / Ultrafast where actually available. Standard is the default. Speed does not change the recommended reasoning strength.
- **Expected comprehensive cost:** relative price-weighted cost of the whole route, separate from chosen strength and raw token usage. Never imply X-High is a fixed quantity of credits or tokens.

API defaults, model-catalog defaults, and the router's recommendation are different. An API benchmark setting is evidence about that tested configuration, not a picker instruction. [Product controls](https://learn.chatgpt.com/docs/models)

## Whole-task routing first

Choose the model for the requested outcome, not for artificially tiny slices. Default to one overall prompt: Luna X-High for bounded work it can complete reliably; GPT-6.1 Sol Medium for coupled decisions and integration; High for difficult diagnosis, conflicting evidence or costly hidden errors; X-High only for a concrete depth benefit. Astra needs an identified capability gap. These are judgments, not guaranteed thresholds.

For substantial delegable work, recommend a capable host with GPT-6 Luna / X-High workers. Put the necessary host and worker responsibilities inside the copyable task prompt. Any concrete worker count or split actually recommended outside the prompt must also appear inside it; otherwise let the host discover scope and allocate details. Do not force a count or exhaustive packages. Simple tasks stay single-agent, and tightly coupled complex tasks may also stay single-agent.

Use current available settings and concrete task evidence. Missing thread context, inaccessible files and repeated ungrounded prompts are not solved by higher effort. Diagnose repeated failures before suggesting a model change. Keep cost reasoning outside the copyable task prompt.

## Select after translating the task

First establish the requested outcome, known inputs, interacting constraints, uncertainty, execution boundary, and how easy mistakes are to detect. Compare credible candidates that preserve completeness, quality, and completion efficiency. Include context reads, reasoning, tool work, retries, handoffs, review, and final integration at the applicable rates. Do not assign artificial complexity scores, failure probabilities, or timing guarantees.

For a complex task with substantial bounded execution or evidence-gathering parts, compare **one Sol/Astra host plus Luna X-High workers** with direct host execution. Read [hybrid-delegation.md](hybrid-delegation.md) only when that candidate is plausible. Delegability alone is insufficient: workers must fit Luna's capability, handoffs must stay compact, and the host must avoid duplicating the same work. More worker tokens do not disqualify a route if weighted cost is lower and quality/efficiency are preserved. Reject a cheaper arrangement likely to reduce reliability or slow overall completion.

| Task | Starting choice | Upgrade or alternative condition |
|---|---|---|
| Clear-source extraction, rewriting, summaries, repeated classification | GPT-6 Luna X-High | 6.1 Sol Low if meaning, omissions, or inconsistent instructions need stronger interpretation. |
| Scoped code/SQL edits with known intent and reviewable results | Luna X-High | 6.1 Sol Medium if causes, dependencies, or correctness span multiple components. Preserve any instruction not to run the code/query. |
| Ambiguous spoken request with context, competing priorities, or important implicit references | 6.1 Sol Low/Medium | Low for semantic cleanup; Medium for resolving coupled decisions. Do not charge for irrelevant downstream work. |
| Cross-source research, contradictory evidence, comparative recommendations | 6.1 Sol Medium | High when evidence conflicts materially or omissions are costly; X-High for unusually difficult reconciliation. |
| Broad repository changes, uncertain root causes, sustained tool workflows | 6.1 Sol Medium | High for deeper diagnosis; X-High when demanding review/depth has a concrete benefit. |
| Connected documents, presentations, design systems, multi-deliverable work | 6.1 Sol Medium/High | Judge actual artifact quality. A text or presentation benchmark does not establish image-generation/design superiority. |
| Novel scientific reasoning, hard mathematics, adaptation to unfamiliar interactive environments | 6.1 Sol High/X-High versus Astra Low/Medium | Prefer Astra when its domain capability or a demonstrated Sol failure addresses a material gap. Raise Astra effort only for a depth requirement. |
| Exacting final review with expensive hidden errors | 6.1 Sol High/X-High versus Astra Medium/High | Astra when independent judgment/domain depth is worth the extra consumption; not just because the word "important" appears. |
| Complex task with substantial independent or stable bounded parts | 6.1 Sol host plus Luna X-High workers; Astra host for a concrete capability gap | Use the hybrid gate; one overall prompt authorizes Luna X-High workers as needed and keeps final ownership with the host. Let the host discover and allocate packages. |
| Large amounts of independent, stable repeated work | Luna X-High directly if it can complete the whole outcome | Add a Sol/Astra host only if real coordination or judgment needs justify its overhead while preserving efficiency. |

[Official task guidance](https://learn.chatgpt.com/docs/model-selection) supports this general placement. The specific thresholds above are routing inferences. A long task may be easy repetition; a short task may have hard uncertainty. Missing inputs, broken tools, or unreadable project context require access/context repair, not a stronger model.

## Resolve overlapping candidates

| Overlap | Default preference | Reason to choose the other |
|---|---|---|
| Luna X-High vs 6.1 Sol Low | Luna for explicit, bounded, easily checked work | Sol Low for semantic ambiguity or omissions Luna is likely to repeat. Its stronger composite result does not automatically justify every small task. |
| Luna X-High vs 6.1 Sol Medium | Luna for the whole bounded task; Sol for coupled uncertain decisions | Hybrid when a host is necessary and substantial bounded work can move to Luna without harming quality/efficiency. Include handoffs and integration. |
| 6.1 Sol Medium vs old 6 Sol X-High | 6.1 Sol Medium | Same ordinary credit rates, stronger current composite evidence; old Sol when unavailable new model or reproducible task-specific regression. No universal per-task saving asserted. |
| 6.1 Sol Low/Medium vs 5.6 Sol High/X-High | 6.1 Sol ordinarily | Retain 5.6 Sol for demonstrated strengths on this user's knowledge/reasoning/format tasks or compatibility. Neither aggregated scores nor model age prove dominance. |
| 6.1 Sol High/X-High vs Astra Low/Medium | Sol for coding, documents, automation without an identified gap | Astra for novel science, abstract adaptation, or comparable failures that deeper Sol reasoning does not resolve. Equal composite scores do not mean identical specialties. |
| 6 Luna X-High vs 5.6 Luna X-High | 6 Luna ordinarily | 5.6 Luna for a repeatable quality advantage large enough to offset its higher rates. The small composite-score difference is insufficient by itself. |
| 6.1 Sol vs 5.6 Terra / 5.5 | 6.1 Sol ordinarily | Legacy compatibility or observed task-specific advantage. There is no general cost advantage in the current credit rate card. |

Do not always start with a small model and upgrade only after failure: when coupling or recovery risk is already evident, route directly to Sol. Do not automatically assign Astra to all difficult work. For a close choice, explain the winner and a concrete switch condition in one or two sentences. Ordinary recommendations need at most one sentence of rationale, not a full comparison.

## Choose strength independently

- **Low:** focused interpretation, edits, straightforward tool work where model capability matters more than depth.
- **Medium:** coordinated coding, research, planning, and completeness; normal Sol starting point, not an excuse to bypass Luna for routine work.
- **High:** non-obvious causes, conflicting evidence, interacting constraints, substantial verification.
- **X-High:** unusually demanding single-agent reasoning/review with an identifiable benefit over High.
- **Ultra:** availability-dependent delegation decision, not the next item on this strength ladder. Avoid for one tightly coupled reasoning problem.

Higher strength can add consumption without improving results. If the issue is a capability/domain gap, compare a stronger model at moderate strength; if it is inadequate checking within existing capability, compare increased strength. Do not resolve missing information by requesting more thinking.

## Economy and speed

Only when the user asks for a cost forecast, report **低 / 中 / 高** as a qualitative forecast of comprehensive whole-task cost, not a numeric quota or raw token count. In hybrid work weight each worker's usage by its own rates and include host planning, review, integration, retries, and billable services. More parallelism can change elapsed time, tokens, and cost in different directions. Higher token usage on Luna can still be cheaper; do not reject it on token count alone. Mark forecasts provisional when material inputs or billing are unknown.

Separate included subscription allowance, purchased/workspace credits, and API charges. Credit-rate ratios compare identical token mixes only; benchmarks compare their own task distributions only. Neither establishes this user's allowance depletion. Use actual recorded consumption when available, not guessed task prices.

Standard is default, not a requirement to accept slower completion for lower cost. Choose an available faster speed when needed for the user's efficiency requirement or preference and account for its billing. As of the September 30 check, 6.1 Sol had Standard/Fast; Ultrafast was forthcoming. Refresh availability before selecting it. Astra Ultrafast has eligibility limits. Never infer a hidden strength from speed. [Speed and billing](https://learn.chatgpt.com/docs/agent-configuration/speed)

## Evidence and ongoing calibration

Keep official facts, independent measurements, user preferences, availability, and judgments separate. Use current comparable benchmark versions and configurations; do not infer missing chart values or transfer scores between models. Refresh affected evidence on releases, policy changes, picker conflicts, or when stale data decides a close choice.

6.1 Sol is newly released: official and AA evidence is useful, while cross-benchmark coverage and this user's controlled comparisons remain incomplete. Legacy strengths are reasons to preserve comparison candidates, not to invent specialties. GPT-5.5 retires from signed-in Codex on 2026-10-14; API availability is separate. [Models](https://learn.chatgpt.com/docs/models)

For future real-task calibration, record the same starting inputs, user-stated completion conditions, model/strength/speed, material errors/omissions, correction rounds, per-model usage and applicable prices or observed billing when accessible, and total completion time. Compare only meaningful overlap pairs. Do not run billable multi-model experiments or send prompts to other chats merely to validate a recommendation without authorization. Treat isolated outcomes as provisional and retain task-family differences.
