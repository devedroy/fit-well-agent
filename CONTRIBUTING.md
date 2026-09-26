# Contributing to FitWell Agent

Thank you for your interest in contributing to **FitWell Agent**! 🎉

We welcome contributions of all kinds: bug reports, documentation updates, feature requests, and code enhancements.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to [devedroy.dr@gmail.com](mailto:devedroy.dr@gmail.com).

---

## How Can I Contribute?

### 1. Reporting Bugs
- Search existing [Issues](https://github.com/devedroy/fit-well-agent/issues) to verify if the bug has already been reported.
- If not, create a new issue using our **Bug Report** template.
- Include detailed steps to reproduce the issue, your operating system, Python version, and relevant terminal/console logs.

### 2. Suggesting Features
- Open an issue using the **Feature Request** template.
- Clearly describe the proposed feature, the use case, and any alternatives considered.

### 3. Pull Requests

1. **Fork the Repository**:
   Click "Fork" on GitHub and clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/fit-well-agent.git
   cd fit-well-agent
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Set Up Development Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

4. **Make Your Changes**:
   - Write clean, readable code conforming to [PEP 8](https://peps.python.org/pep-0008/).
   - Keep privacy in mind: never hardcode sensitive keys or send user profile data to unnecessary external endpoints.
   - Test your changes locally by running `python run.py`.

5. **Commit Your Changes**:
   Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new functionality
   - `fix:` for bug fixes
   - `docs:` for documentation updates
   - `refactor:` for code restructuring without behavior changes
   - `chore:` for maintenance or dependency updates

   Example:
   ```bash
   git commit -m "feat(agent): add support for additional fitness metrics"
   ```

6. **Submit a Pull Request**:
   - Push your branch to GitHub:
     ```bash
     git push origin feature/my-new-feature
     ```
   - Open a PR against the `main` branch of `devedroy/fit-well-agent`.
   - Fill out the PR template completely.

---

## Attribution & Licensing

By contributing code to FitWell Agent, you agree that your contributions will be licensed under the [MIT License](LICENSE).
