# Claude Code Guidelines

@AGENTS.md

---

## Claude Code Specific Instructions

1. **Governance Inheritance:** All universal invariants defined in [`AGENTS.md`](AGENTS.md) apply to every Claude Code session without exception.
2. **Local Operator Settings:** If `CLAUDE.local.md` is present in the repository root, load it for private operator-specific preferences. Never stage or commit `CLAUDE.local.md` (enforced via `.gitignore`).
3. **Scoped Rules:** Consult path-scoped rules in `.claude/rules/` when touching matching files:
   - Documentation & Presentation: [`.claude/rules/docs.md`](.claude/rules/docs.md) (applies to `docs/**`, `README.md`, `DESIGN.md`)
   - Brand Assets & Media: [`.claude/rules/brand.md`](.claude/rules/brand.md) (applies to `assets/**`)
4. **Context & Compaction:** When running extended workflows, avoid re-reading unchanged files repeatedly. Rely on compact diff summaries and preserve context space for reasoning and verification.

