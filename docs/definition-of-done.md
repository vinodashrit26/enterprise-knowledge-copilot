# Definition of done

A change is done only when every item below is true. If an item does not apply, the pull request says "N/A" and gives the reason.

## For every change
- [ ] The work was done on a branch and merged through a pull request, with the template filled in honestly.
- [ ] CI is green: Ruff, format check, mypy, pytest (coverage at least 85%) and bandit.
- [ ] Pre-commit hooks pass locally, and were not bypassed with `--no-verify`.
- [ ] Tests were added or updated. A bug fix starts with a test that fails first.
- [ ] No secrets or private data are committed. `.env` stays local, and `.env.example` is updated when settings change.
- [ ] Documentation is updated (README, decision records, requirements), or marked N/A with a reason.
- [ ] The pull request states what was not tested, and the real risks.
- [ ] The pull request title is a clear Conventional Commit message, and the merge is a squash merge.

## For AI features (from Phase 2 onward)
- [ ] New scenarios are added to the golden evaluation set, including at least one unanswerable and one adversarial case.
- [ ] Results are measured against the targets in `docs/product-vision.md` and the evaluation plan, and failures are analyzed.
- [ ] Latency and cost per task are measured and recorded.
- [ ] Any change to a prompt, model or retrieval setting is compared against the previous version before it is accepted.
- [ ] Security tests (tenant isolation, prompt injection, approval bypass) pass.

## Not done if
- CI is red or skipped, or a check was weakened to make it pass.
- A claim in the pull request, README or a document is not backed by a test, a measurement or a source.
