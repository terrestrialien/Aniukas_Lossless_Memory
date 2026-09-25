# Contributing

Contributions to the design, schemas, tests, documentation, translations, integrations, and future reference implementation are welcome. Fork the repository to adapt it to your own systems and hardware. Your changes belong in your copy; maintainers decide which proposed changes become part of the maintained original.

## Contribution workflow

1. For a substantial design change, open an issue describing the behavior and affected requirement IDs.
2. Create a branch in your fork, make the change, and update any affected schemas, examples, requirement mappings, and acceptance scenarios together.
3. Run `python tools/check_all.py` in an environment with `requirements-dev.txt` installed.
4. Submit a pull request explaining the problem, resulting behavior, affected requirement IDs, tests, and remaining limits.

When changing a requirement, record the new behavior and its effect on existing implementations. Preserve stable IDs or provide an explicit migration mapping. Do not erase a required capability merely because it is inconvenient to implement.

## Claims and compatibility

This release is a specification and contract kit. Label runtime implementations and partial profiles accurately. Include a feature matrix and acceptance evidence before claiming conformance. A tool that validates example files does not demonstrate model recall, authorization enforcement in a running service, crash safety, or performance.

Changes to the portable format require an explicit version/migration decision. Preserve complete source bytes, identities, revision meaning, and evidence references. Explain compatibility implications rather than silently changing fields or enum meanings.

Use synthetic conversations and test principals. Keep personal logs, credentials, operational memory, and machine-specific paths outside public contributions.

## License and credit

Contributions are provided under the same [MIT License](LICENSE) as the whole package. Contributors retain copyright in their contributions; no copyright assignment is required. Preserve existing notices and attribution to **Andrius Cincys** for the original concept and system architecture. Identify any third-party material and its applicable terms.

Private modifications need not be submitted upstream. Public forks do not grant write access to the maintained original. Propose upstream changes through a pull request with the relevant checks passing; maintainers review changes before merging them.
