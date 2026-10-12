# Claude Code Guidelines

@AGENTS.md

---

## Claude Code Specific Instructions

1. **Governance Inheritance:** All universal invariants defined in [`AGENTS.md`](AGENTS.md) apply to every Claude Code session without exception.
2. **Context & Compaction:** When running extended workflows, rely on compact diff summaries and preserve context space for reasoning and verification.
3. **Scoped Rules:** Consult path-scoped rules in `.claude/rules/` when touching matching files:
   - Documentation: [`.claude/rules/docs.md`](.claude/rules/docs.md) (applies to `docs/**`, `README.md`, `DESIGN.md`)
   - Brand Assets: [`.claude/rules/brand.md`](.claude/rules/brand.md) (applies to `assets/**`)
   - Licensing & Source Headers: [`.claude/rules/licensing.md`](.claude/rules/licensing.md) (applies to `scripts/**`, `src/**`)
