# Contributing Guide

Thank you for your interest in contributing to the **Awesome XRAI for Architecture** repository! This document will guide you through the contribution process.

## 🚨 Important: All contributions require approval

All changes to this repository must be reviewed and approved by the repository maintainer before being merged. This ensures quality and consistency of the research database.

## 🤝 How to Contribute

### For External Contributors (Recommended)

1. **Fork the repository** on GitHub

2. **Clone your fork locally:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/Awesome-XRAI-for-Architecture.git
    cd Awesome-XRAI-for-Architecture
    ```

3. **Create a new branch for your contribution:**

   ```bash
   git checkout -b add-new-papers
   # or
   git checkout -b fix-paper-info
   ```

4. **Make your changes** (see sections below)

5. **Push to your fork:**

    ```bash
    git push origin add-new-papers
    ```

6. **Create a Pull Request** on GitHub

7. **Wait for review and approval** - The maintainer will review your changes

8. **Address any feedback** if requested

9. **Your PR will be merged** after approval

### For Repository Collaborators

If you have been added as a collaborator:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/prakashknaikade/Awesome-XRAI-for-Architecture.git
   cd Awesome-XRAI-for-Architecture
   ```

2. **Create a new branch:**

   ```bash
   git checkout -b your-feature-branch
   ```

3. **Make changes and create a Pull Request** (never push directly to `main`)

## Adding Papers

We use a custom database editor to maintain the paper database. To add or edit papers:

### Method 1: Using the Web-Based Editor (Recommended)

This runs a local web application that allows you to easily manage papers from any browser, with no display server or external GUI dependencies required.

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Run the editor:

    ```bash
    python editor.py
    ```

3. Open your browser and navigate to the address shown in the terminal (usually `http://localhost:8000`).

4. Use the web interface to:
   - Add new papers manually (with instant form validation and tag selector buttons).
   - Fetch metadata automatically using the **arXiv Details Fetcher** (just input any arXiv URL or ID).
   - Edit, delete, or filter existing entries.
   - Click **Save Database** to save changes, which automatically regenerates the site pages (`index.html` and `analytics.html`) and the repository `README.md`.

---

### Method 2: Using the Desktop App (Alternative)

If you prefer a traditional desktop GUI, you can launch the PyQt6-based application. Note that this requires a local display server.

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Install Poppler (required for PDF thumbnail processing inside the desktop client):
    - **Ubuntu/Debian:**

      ```bash
      sudo apt-get install poppler-utils
      ```

    - **macOS:**

      ```bash
      brew install poppler
      ```

    - **Windows:**
      - Download and install from: <https://github.com/oschwartz10612/poppler-windows/releases/>
      - Add the `bin` directory to your system PATH

3. Run the desktop editor:

    ```bash
    python editor.py --desktop
    ```

---

### Method 3: Manual YAML Editing

If you prefer to edit the YAML file directly, add your paper entry to `awesome_xrai_architecture_papers.yaml` using the following format:

```yaml
- id: "charles2011bim"
  title: "BIM Handbook: A Guide to Building Information Modeling for Owners, Managers, Designers, Engineers and Contractors"
  authors: ["Charles M. Eastman"]
  year: 2011
  venue: "John Wiley & Sons" # optional
  paper_url: "https://books.google.com/books?id=-GjrBgAAQBAJ"
  code_url: "https://github.com/username/repo"    # optional
  project_url: "https://project-website.com"     # optional
  tags: ["3D Reconstruction", "BIM", "Quality Control and Validation"]
  primary_category: "Reality Capture and Digital Twins"
  abstract: "Building Information Modeling (BIM) offers a novel approach to design, construction, and facility management..."
```

### Required Fields

- `id`: A unique kebab-case ID (usually `firstauthorYEARshorttitle`, e.g. `charles2011bim`).
- `title`: Complete paper title.
- `authors`: List of authors (formatted as a YAML array).
- `year`: Publication year (integer).
- `paper_url` (or `paper`): Direct URL to the paper's PDF, publisher page, or abstract page.
- `primary_category`: The main category the paper belongs to (must match one of the categories below).
- `abstract`: Brief description of the paper and its contributions.

### Optional Fields

- `venue`: Conference or journal name.
- `code_url`: Link to the open-source code repository (e.g. GitHub).
- `project_url`: Link to the project or research page.
- `tags`: Additional descriptive tags or labels.

### Paper Categories

To maintain organization, the `primary_category` field must match one of the following exactly:

- `AI-Driven Design and Generative Architecture`
- `Reality Capture and Digital Twins`
- `Computational BIM and Intelligent Operations`
- `Heritage Conservation and Cultural Preservation`
- `Sustainability and Environmental Performance`
- `Sustainable Real Estate Valuation and Economics`
- `Human-Computer Interaction and Human-Building Interaction`

## 🔧 Testing Your Changes

Before submitting a PR, please test your changes:

1. **Validate YAML syntax:**

   ```bash
   python -c "import yaml; yaml.safe_load(open('awesome_xrai_architecture_papers.yaml'))"
   ```

2. **Test HTML generation:**

   ```bash
   python src/generate.py awesome_xrai_architecture_papers.yaml index.html
   ```

   Open the generated index.html file in browser and check for any mistakes.

3. **Generate updated README (Important):**

   ```bash
   python generate_readme.py
   ```

## 📋 Pull Request Guidelines

### PR Requirements

- **Clear description** of what you're adding/changing
- **Working links** to papers and resources
- **Appropriate categorization** and tags
- **Proper formatting** following existing style
- **One topic per PR** (don't mix unrelated changes)

## 🚫 What NOT to Include

Please don't add:

- Papers not related to XR/AI in Architecture
- Broken or inaccessible links
- Duplicate entries
- Incomplete information (missing abstracts, authors, etc.)
- Personal projects without peer review (unless in appropriate section)

## 🛠️ Adding Other Resources

For non-paper resources (tools, datasets, tutorials):

1. **Fork and create a branch**
2. **Edit the appropriate section** in README.md
3. **Follow existing formatting**
4. **Create a Pull Request**

## 🆘 Need Help?

- **Check existing issues** on GitHub
- **Look at recent PRs** for examples
- **Create an issue** if you're unsure about something
- **Ask questions** in your PR description

---

## ⚖️ Code of Conduct

By contributing to this repository, you agree to:

- Provide accurate and verifiable information
- Respect intellectual property rights
- Follow the contribution guidelines
- Be respectful in all interactions
- Wait for approval before merging changes

Thank you for helping make this resource better for the XRAI Architecture community! 🏗️✨
