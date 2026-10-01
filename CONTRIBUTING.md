# Contributing to CivixRecord-OS

We welcome contributions from developers, civic technologists, and open-governance advocates.

## Development Workflow

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feat/my-new-feature
   ```

2. Install local development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Ensure all hermetic tests pass:
   ```bash
   pytest civixrecord/tests
   ```

4. Format and lint code:
   ```bash
   ruff check civixrecord
   ```

5. Submit a Pull Request targeting `main`.

## Code Guidelines
- **Hermetic Testing:** No live socket or network dependencies in unit tests.
- **Pure Facts:** Procedural parsers must extract verifiable timestamps and literal quotes.
- **Statutory Fences:** Automated in-camera detection must remain inviolate.
