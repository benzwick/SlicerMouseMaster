# ADR-011: Documentation Infrastructure

## Status

Accepted

## Context

SlicerMouseMaster needs comprehensive documentation for:
- End users learning to configure the extension
- Developers contributing to the project
- The Slicer Extension Index submission

We need to choose:
1. Documentation tooling
2. Hosting platform
3. Documentation structure

## Decision

### Documentation Tooling

We will use **Sphinx with the Read the Docs theme**:

- **Sphinx**: Python documentation standard, mature tooling
- **sphinx-rtd-theme**: Clean, responsive design familiar to Python developers
- **MyST Parser**: Enables Markdown support alongside reStructuredText

Rationale:
- Matches Slicer core documentation tooling
- Enables future migration to official Slicer docs if desired
- Supports both .rst and .md files
- Rich extension ecosystem (autodoc, viewcode, etc.)

### Hosting

We will use **GitHub Pages** with automatic deployment:

- Free hosting for open source projects
- Integrated with GitHub Actions CI/CD
- Custom domain support if needed
- No external service dependencies

Alternative considered: Read the Docs
- Pro: Automatic builds, version support
- Con: Additional service to maintain, may have availability issues

### Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Landing page
├── user-guide/          # End user documentation
├── developer-guide/     # Contributor documentation
├── reference/           # API and format reference
└── adr/                 # Architecture decisions
```

Rationale:
- Clear separation between user and developer content
- Reference section for technical specifications
- ADRs included in documentation site

### File Formats

- Use **.rst** for structured documentation (indexes, tables)
- Use **.md** for prose-heavy content (ADRs, guides)
- MyST parser enables mixing both formats

### Screenshots

- Stored in `Screenshots/` directory (repository root level)
- Referenced via relative paths from docs
- Single source of truth for Extension Index and documentation

## Consequences

### Positive

- Professional documentation site
- Automatic deployment on merge to main
- Support for versioned documentation in future
- Familiar tooling for Python/Slicer developers
- Screenshots in one location avoid duplication

### Negative

- Additional build step in CI
- Contributors need to learn Sphinx/RST basics
- Initial setup complexity

### Neutral

- Need to maintain both README.md (GitHub landing) and docs site
- Documentation updates require building locally to preview

## Implementation

1. Create `docs/conf.py` with Sphinx configuration
2. Create `docs/requirements.txt` for doc dependencies
3. Create `.readthedocs.yaml` for RTD compatibility
4. Create `.github/workflows/docs.yml` for GitHub Pages deployment
5. Create documentation content in `docs/` subdirectories
6. Update README.md to link to hosted documentation

## References

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [GitHub Pages](https://pages.github.com/)
- [Slicer Documentation](https://slicer.readthedocs.io/)
