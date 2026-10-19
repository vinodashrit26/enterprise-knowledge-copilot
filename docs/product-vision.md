# Product vision

## Who it is for
Nancy (a fictional persona) is an operations engineer responsible for onboarding enterprise customers onto a document-management platform. When onboarding gets stuck, she must manually investigate scattered information to find the likely root cause. This is slow, hard to repeat, and prone to missed evidence and wrong conclusions. A single missing permission or overlooked prerequisite can delay a customer by days.

## What the product does
The Enterprise Knowledge & Workflow Copilot helps operations engineers investigate stuck onboardings. Using approved, read-only tools, it retrieves information from runbooks, troubleshooting guides, configuration records, prerequisite checklists, application logs, API integration status, and past support cases.

It correlates the evidence, identifies likely root causes, checks prerequisites, and highlights missing or conflicting information. It produces a structured investigation report with source citations and recommended next steps. When the evidence is insufficient, it says so instead of guessing. It proposes safe remediation plans, but engineers stay in control: every state-changing action requires explicit human approval. Investigations, evidence, decisions, and actions are recorded for audit.

## How we will know it works
All numbers below are targets, not results. They will be measured on a golden evaluation set of synthetic scenarios.

**Targets**
- Retrieval Recall@5: at least 90% of required evidence items found in the top five results (scoring method defined in the evaluation plan).
- Evidence support: at least 95% of answers supported by the cited evidence.
- Citation correctness: at least 95%.
- Abstention: at least 90% correct "insufficient evidence" answers on questions that cannot be answered reliably.
- Investigation completion: at least 85% of in-scope investigation tasks completed successfully.

**Safety targets (tested with adversarial scenarios, including prompt injection)**
- Zero cross-tenant retrievals.
- Zero unapproved state-changing actions.
- Zero duplicate actions on retry.

**Also measured (targets will be set in the evaluation plan)**
- Retrieval Precision@5.
- Root-cause accuracy: the identified cause matches the expected diagnosis and is supported by evidence.
- Multi-step reliability: tool-call correctness and recovery from tool errors.
- Clarification: when a request is ambiguous or incomplete, the copilot asks a specific question instead of guessing, and does not ask when the information is already available.

**Business outcome.** The main outcome is reducing the time needed to reach a justified root cause. The baseline is one engineer manually searching the same sample documents on the same scenarios. Where useful, simpler keyword-search or rules-based approaches will also be compared, to show what the AI adds. Time to a justified root cause, diagnostic correctness, and evidence quality will be compared. Results will be reported as simulated evaluation results, not as real-world customer impact.

## What it is not
- Not autonomous: no state-changing action without explicit human approval.
- Not a general-purpose chatbot: focused on onboarding investigations and safe remediation.
- Not production-connected in this project: uses synthetic data, not real customer data.
- Not a replacement for engineers or existing tools: supports engineering judgment and complements current workflows.

## When not to use AI
Use deterministic application code for exact checks, such as certificate expiry, configuration lookups, and permission checks. AI interprets evidence and proposes resolutions. Application code enforces authorization, validation, and approval controls.

## Main risks
- **Incorrect root cause.** Risk: a wrong conclusion presented with confidence. Mitigation: evidence-backed conclusions, citations, and "insufficient evidence" answers.
- **Cross-tenant data exposure.** Risk: one tenant's evidence appears in another tenant's answer. Mitigation: enforce tenant isolation in code and test it automatically.
- **Prompt injection.** Risk: malicious instructions in retrieved documents manipulate the copilot or its tool use. Mitigation: treat retrieved content as untrusted data, use read-only tools by default, test adversarial scenarios, and enforce authorization and tool limits in code, independent of model instructions.
- **Unsafe autonomy.** Risk: an unintended state-changing action. Mitigation: require human approval and enforce authorization before execution.
