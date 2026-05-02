# Policy

## Repository Role

This repository is a public chronology and hash-commitment surface.

It is used to publish:
- author-declared evaluation plans that are safe to disclose publicly
- hashes of released evidence packages
- later links to external transparency-log entries

It is not used to claim:
- that a post-study commit is preregistration
- that Git timestamps alone prove scientific priority beyond the public repository surface
- that a release DOI is a pre-execution registry timestamp

## Operating Rules

1. History is append-only. Do not force-push or rewrite prior commitment commits.
2. Each campaign gets a dated directory under `commitments/`.
3. Each commitment directory should contain a machine-readable manifest, a short human-readable note, and any public source surfaces copied verbatim.
4. If an external transparency log is used, record the entry ID, verification command, and date in the same campaign directory.
5. If a commitment is post-study, say so explicitly.

## NISQ Boundary

The first NISQ entry in this repository is a post-study public commitment created after execution and after Zenodo publication. It improves public chronology and future workflow discipline, but it does not change the preregistration status of the current NISQ paper.