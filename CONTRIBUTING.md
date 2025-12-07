# Welcome to *Food Seer* Contributing Guide

We're thrilled you're interested in contributing to our [project](https://github.com/rishi082000/CSC510-Section2-Group7-Proj3)! This guide outlines the steps for getting involved, from submitting issues to crafting and merging pull requests.

Before you begin, please take a moment to read our [Code of Conduct](https://github.com/rishi082000/CSC510-Section2-Group7-Proj3/blob/main/CODE_OF_CONDUCT.md). It’s essential for fostering a respectful, inclusive, and collaborative community.

---

## Table of Contents
1. [How Can I Contribute?](#how-can-i-contribute)
2. [Submitting a Pull Request](#submitting-a-pull-request)
3. [Coding Standards](#coding-standards)
4. [Contributor IP & Copyright](#contributor-ip--copyright)

---

## How Can I Contribute?

#### 1. Discuss Changes
- Before making any changes, please share your idea with the project maintainers. You can do this by opening a [new issue](https://github.com/rishi082000/CSC510-Section2-Group7-Proj3/issues), sending an email, or contacting the team through the channels listed in the [README](https://github.com/rishi082000/CSC510-Section2-Group7-Proj3/blob/main/README.md).

#### 2. Creating Issues
- Before filing a new issue, take a moment to review the [existing issue list](https://github.com/rishi082000/CSC510-Section2-Group7-Proj3/issues) to avoid duplicates.
- If you're reporting a bug, please use the provided bug report template and include as much detail as possible to help us reproduce and resolve the problem efficiently.

#### 3. Addressing Code of Conduct Violations
- If you witness or experience behavior that breaches our Code of Conduct, please notify the project maintainers. Contact information is available in the [README](https://github.com/rishi082000/CSC510-Section2-Group7-Proj3/blob/main/README.md).

---

## Submitting a Pull Request

1. **Fork and Clone**: Begin by forking the repository and cloning it to your local development environment.
2. **Create a New Branch**: Create a new branch with a descriptive name that reflects your changes, e.g., `bugfix-issue-1`.
3. **Implement Your Changes**: Make your updates while adhering to the project's coding standards and best practices outlined below.
4. **Write and Run Tests**: If your changes introduce new functionality or fix a bug, include appropriate tests. Make sure all tests pass locally before proceeding.
5. **Open a Pull Request**: Once your changes are ready, push your branch and open a pull request. Use a clear, concise title and provide a detailed description. Be sure to fill out the PR template to streamline the review process.

---

## Coding Standards

To maintain code quality across the Food Seer project, please follow these coding standards for both backend (Java) and frontend (JavaScript/React) development:

### Backend (Java) Standards

- **Code Formatting**: We use **Google Java Format** for consistent code style. Format your code before submitting:
```bash
# Using Maven plugin
mvn com.coveo:fmt-maven-plugin:format

# Or download and use google-java-format JAR
java -jar google-java-format.jar --replace $(find . -name "*.java")
```

- **Linting**: We use **Checkstyle** to enforce Java coding conventions. Run Checkstyle locally and resolve any reported issues:
```bash
# Using Maven
mvn checkstyle:check

# View the report
open target/site/checkstyle.html
```

- **Static Analysis**: **SpotBugs** is used to identify potential bugs and code quality issues:
```bash
# Using Maven
mvn spotbugs:check

# Generate GUI report
mvn spotbugs:gui
```

- **Code Quality Standards**:
  - Follow Java naming conventions (camelCase for methods/variables, PascalCase for classes)
  - Maximum method complexity: 10 (cyclomatic complexity)
  - Maximum line length: 120 characters
  - All public methods must have Javadoc comments
  - Use meaningful variable and method names

### Frontend (JavaScript/React) Standards

- **Code Formatting**: We use **Prettier** for automatic formatting. Run Prettier before submitting your code:
```bash
# Format all files
npm run format

# Or run Prettier directly
npx prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,md}"
```

- **Linting**: We use **ESLint** to enforce code quality and catch potential errors:
```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

- **Type Checking** (if using TypeScript):
```bash
# Run type checking
npm run type-check
```

---

## Contributor IP & Copyright

### Do contributors keep the copyright/IP of their contributions?

Yes — contributors retain ownership of their own contributions.

By contributing code, documentation, or other content to this repository, you agree that:

- **You still own the intellectual property for your contributions**
- You grant the project maintainers a license to use, modify, and distribute your contributions as part of the project
- You confirm that your contributions are original or appropriately licensed by you

This model encourages open collaboration while protecting contributor rights.


- **Code Quality Standards**:
  - Follow Airbnb JavaScript Style Guide
  - Use functional components with hooks (avoid class components)
  - Maximum function complexity: 10
  - Maximum line length: 100 characters
  - Prop validation required for all components (PropTypes or TypeScript)
