# Contributing to SudoMode 🛡️

Thank you for your interest in contributing to SudoMode! We're excited to have you on board. This guide will help you get started.

## 🚀 Quick Start

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page. This creates a copy of the repository in your GitHub account.

### 2. Clone Your Fork

```bash
git clone https://github.com/yourusername/sudomode-ai.git
cd sudomode-ai
```

### 3. Create a Branch

Create a new branch for your feature or fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 4. Make Your Changes

- Write clean, well-commented code
- Follow the code style guidelines (see below)
- Add tests if applicable
- Update documentation as needed

### 5. Commit Your Changes

```bash
git add .
git commit -m "Add: description of your changes"
```

**Commit message format:**
- `Add: feature description` - for new features
- `Fix: bug description` - for bug fixes
- `Update: what was updated` - for updates
- `Docs: documentation changes` - for documentation

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Submit a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - What you changed and why
   - How to test your changes
   - Screenshots (if UI changes)

## 🛠️ Tech Stack

Understanding the tech stack will help you contribute effectively:

### Backend (Server)
- **FastAPI** - Modern Python web framework for building APIs
- **Python 3.11+** - Programming language
- **Pydantic** - Data validation using Python type annotations
- **SimpleEval** - Safe expression evaluation for policy conditions
- **PyYAML** - YAML parser for policy configuration
- **Uvicorn** - ASGI server for running FastAPI

**Location:** `server/` directory

### Frontend (Dashboard)
- **React 19** - UI library for building user interfaces
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript/JSX** - Programming language

**Location:** `dashboard/` directory

### SDK (Client Library)
- **Python 3.11+** - Programming language
- **httpx** - HTTP client library for making API requests
- **Pydantic** - Data validation

**Location:** `sdk/` directory

## 📝 Code Style

### Python (Backend & SDK)

- Follow **PEP 8** style guide
- Use **type hints** where possible
- Add **docstrings** to functions and classes
- Keep functions focused and small
- Use meaningful variable names

**Example:**
```python
def evaluate_request(
    self, 
    request: GovernanceRequest
) -> GovernanceResponse:
    """
    Evaluate a governance request against policy rules.
    
    Args:
        request: The governance request to evaluate
        
    Returns:
        GovernanceResponse with status and reason
    """
    # Implementation here
```

### JavaScript/React (Frontend)

- Follow **ESLint** rules (already configured)
- Use **functional components** with hooks
- Keep components small and focused
- Use meaningful prop and variable names
- Prefer `const` over `let`, avoid `var`

**Example:**
```javascript
function RequestCard({ request, onApprove, onReject }) {
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Component logic here
}
```

## 🧪 Testing

Before submitting a PR, please test your changes:

### Backend Testing
```bash
cd server
# Start the server
uvicorn app.main:app --reload

# Test the API
curl http://localhost:8000/health
```

### Frontend Testing
```bash
cd dashboard
# Start the dev server
npm run dev

# Open http://localhost:5173 and verify UI works
```

### SDK Testing
```bash
cd sdk
# Run examples
python examples/demo_agent.py
```

## 📚 Development Setup

1. **Set up the backend:**
   ```bash
   cd server
   python3.11 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up the frontend:**
   ```bash
   cd dashboard
   npm install
   ```

3. **Set up the SDK:**
   ```bash
   cd sdk
   pip install -r requirements.txt
   ```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

## 🐛 Reporting Bugs

Found a bug? Please open an issue with:

- **Clear title** describing the bug
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Error messages** or logs
- **Screenshots** (if applicable)

## 💡 Suggesting Features

Have an idea? We'd love to hear it! Open an issue with:

- **Clear description** of the feature
- **Use case** - why is this feature needed?
- **Proposed implementation** (if you have ideas)
- **Examples** of how it would be used

## 📖 Documentation

When adding features, please:

- Update the README.md if it's a major feature
- Add docstrings to new functions/classes
- Update examples if API changes
- Add comments for complex logic

## ❓ Questions?

- **Open an issue** with the "question" label
- **Check existing issues** and discussions
- **Review the code** - it's well-commented!

## 🎉 Thank You!

Your contributions make SudoMode better for everyone. We appreciate your time and effort!

**Happy coding!** 🚀
