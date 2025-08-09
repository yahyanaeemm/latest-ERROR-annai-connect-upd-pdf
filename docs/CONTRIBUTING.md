# Contributing to AnnaiCONNECT

## 🎯 Welcome Contributors!

Thank you for your interest in contributing to AnnaiCONNECT! This document provides guidelines and information for contributors to help maintain code quality and consistency.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Harassment of any kind
- Discriminatory language or actions
- Personal attacks or trolling
- Publishing private information without permission
- Other conduct inappropriate in a professional setting

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.11+ installed
- Node.js 18+ installed
- MongoDB 5.0+ running
- Git configured with your username and email
- Code editor with appropriate extensions

### First-Time Setup

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/annaiconnect.git
   cd annaiconnect
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/annaiconnect.git
   ```

3. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   yarn install
   ```

4. **Setup Environment**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   
   # Frontend
   cd frontend
   cp .env.example .env
   # Edit .env with your configuration
   ```

---

## 🛠️ Development Setup

### Development Environment

1. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   
   # Terminal 2 - Frontend
   cd frontend
   yarn start
   ```

2. **Verify Setup**
   - Backend: http://localhost:8001/docs
   - Frontend: http://localhost:3000
   - Database: Ensure MongoDB is running

### Development Tools

#### Recommended VS Code Extensions
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint
- GitLens
- MongoDB for VS Code

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install
```

---

## 📝 Contribution Guidelines

### Types of Contributions

We welcome several types of contributions:

#### 🐛 Bug Fixes
- Fix identified issues
- Improve error handling
- Resolve performance problems

#### ✨ New Features
- Add new functionality
- Enhance existing features
- Improve user experience

#### 📚 Documentation
- Improve existing documentation
- Add missing documentation
- Create tutorials and examples

#### 🧪 Testing
- Add test coverage
- Improve existing tests
- Create integration tests

#### 🔧 Maintenance
- Update dependencies
- Improve code structure
- Optimize performance

### Contribution Workflow

1. **Create an Issue** (for significant changes)
   - Describe the problem or feature
   - Discuss the approach
   - Get feedback from maintainers

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

3. **Make Changes**
   - Follow coding standards
   - Write tests
   - Update documentation

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   python -m pytest tests/
   
   # Frontend tests
   cd frontend
   yarn test
   
   # Integration tests
   python backend_test.py
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "type: brief description"
   ```

6. **Push and Create PR**
   ```bash
   git push origin your-branch-name
   # Create Pull Request on GitHub
   ```

---

## 🎨 Code Standards

### Python (Backend)

#### Style Guide
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://isort.readthedocs.io/) for import sorting
- Use [mypy](http://mypy-lang.org/) for type checking

#### Code Formatting
```bash
# Format code
black server.py

# Sort imports
isort server.py

# Type checking
mypy server.py

# Linting
flake8 server.py
```

#### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "john"
def get_user_by_id(user_id: str) -> User:
    pass

# Classes: PascalCase
class StudentManager:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 50 * 1024 * 1024

# Private methods: _snake_case
def _internal_helper(self):
    pass
```

#### Documentation
```python
def create_student(student_data: StudentCreate, current_user: User) -> Student:
    """
    Create a new student application.
    
    Args:
        student_data: Student information from form
        current_user: Currently authenticated user
        
    Returns:
        Created student object with generated token
        
    Raises:
        HTTPException: If user is not authorized or data is invalid
        
    Example:
        >>> student = create_student(student_data, current_user)
        >>> print(student.token_number)  # AGI2508001
    """
    pass
```

### JavaScript/React (Frontend)

#### Style Guide
- Follow [Airbnb JavaScript Style Guide](https://airbnb.io/javascript/)
- Use [Prettier](https://prettier.io/) for formatting  
- Use [ESLint](https://eslint.org/) for linting

#### Code Formatting
```bash
# Format code
yarn prettier --write src/

# Linting
yarn eslint src/

# Fix auto-fixable issues
yarn eslint src/ --fix
```

#### Component Structure
```jsx
// Imports
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';

// Component
const StudentForm = ({ onSubmit, initialData = null }) => {
  // State declarations
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    course: ''
  });

  // Effects
  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  // Event handlers
  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleInputChange = (field) => (value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Render
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Form content */}
    </form>
  );
};

export default StudentForm;
```

#### Naming Conventions
```jsx
// Components: PascalCase
const StudentDashboard = () => {};

// Variables and functions: camelCase
const userData = {};
const handleButtonClick = () => {};

// Constants: UPPER_SNAKE_CASE
const API_ENDPOINTS = {};

// CSS classes: kebab-case
<div className="student-form-container">
```

### Database (MongoDB)

#### Collection Naming
- Use plural nouns: `users`, `students`, `incentives`
- Use snake_case for multi-word collections: `incentive_rules`

#### Document Structure
```javascript
// User document
{
  id: "uuid-string",
  username: "string",
  email: "string",
  role: "agent|coordinator|admin",
  first_name: "string",
  last_name: "string",
  created_at: ISODate(),
  updated_at: ISODate()
}

// Student document
{
  id: "uuid-string",
  token_number: "AGI2508001",
  agent_id: "uuid-string",
  first_name: "string",
  last_name: "string",
  email: "string",
  phone: "string",
  course: "string",
  status: "pending|verified|coordinator_approved|approved|rejected",
  documents: {
    "id_proof": "file_path",
    "certificates": "file_path"
  },
  created_at: ISODate(),
  updated_at: ISODate()
}
```

---

## 🧪 Testing Requirements

### Backend Testing

#### Unit Tests
```python
# tests/test_student_management.py
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_create_student():
    """Test student creation with valid data."""
    student_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "course": "B.Ed"
    }
    
    response = client.post(
        "/api/students",
        json=student_data,
        headers={"Authorization": f"Bearer {agent_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["token_number"].startswith("AGI")
```

#### Integration Tests
```python
def test_complete_student_workflow():
    """Test complete student workflow from creation to approval."""
    # 1. Agent creates student
    student = create_test_student()
    
    # 2. Coordinator approves
    approve_response = coordinator_approve_student(student["id"])
    assert approve_response.status_code == 200
    
    # 3. Admin final approval
    admin_response = admin_approve_student(student["id"])
    assert admin_response.status_code == 200
    
    # 4. Verify incentive creation
    incentives = get_agent_incentives(student["agent_id"])
    assert len(incentives) > 0
```

### Frontend Testing

#### Component Tests
```jsx
// src/components/StudentForm.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import StudentForm from './StudentForm';

describe('StudentForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  test('renders form fields correctly', () => {
    render(<StudentForm onSubmit={mockOnSubmit} />);
    
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/course/i)).toBeInTheDocument();
  });

  test('submits form with valid data', async () => {
    render(<StudentForm onSubmit={mockOnSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: 'John' }
    });
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: 'Doe' }
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'john@example.com' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@example.com',
        course: ''
      });
    });
  });
});
```

#### E2E Tests
```jsx
// cypress/integration/student_workflow.spec.js
describe('Student Management Workflow', () => {
  beforeEach(() => {
    cy.login('agent1', 'agent@123');
  });

  it('creates and manages student application', () => {
    // Create student
    cy.visit('/dashboard');
    cy.get('[data-testid="add-student-btn"]').click();
    
    cy.get('[name="firstName"]').type('Test');
    cy.get('[name="lastName"]').type('Student');
    cy.get('[name="email"]').type('test@example.com');
    cy.get('[name="course"]').select('B.Ed');
    
    cy.get('[type="submit"]').click();
    
    // Verify creation
    cy.contains('Student created successfully');
    cy.get('[data-testid="student-list"]')
      .should('contain', 'Test Student');
  });
});
```

### Test Coverage

#### Minimum Coverage Requirements
- **Backend**: 80% line coverage
- **Frontend**: 70% line coverage
- **Critical paths**: 95% coverage

#### Running Coverage
```bash
# Backend coverage
cd backend
pytest --cov=. --cov-report=html tests/

# Frontend coverage
cd frontend
yarn test --coverage --watchAll=false
```

---

## 📋 Pull Request Process

### PR Checklist

Before submitting a pull request, ensure:

- [ ] **Code Quality**
  - [ ] Code follows style guidelines
  - [ ] No linting errors
  - [ ] Type hints added (Python)
  - [ ] PropTypes defined (React)

- [ ] **Testing**
  - [ ] All existing tests pass
  - [ ] New tests added for new functionality
  - [ ] Test coverage meets requirements
  - [ ] Manual testing completed

- [ ] **Documentation**
  - [ ] Code is well documented
  - [ ] API documentation updated
  - [ ] User guide updated (if needed)
  - [ ] Changelog updated

- [ ] **Git Hygiene**
  - [ ] Commits are atomic and well-described
  - [ ] Branch is up-to-date with main
  - [ ] No merge conflicts
  - [ ] Sensitive data not committed

### PR Title Format

Use conventional commit format for PR titles:

```
type(scope): brief description

Examples:
feat(student): add bulk import functionality
fix(auth): resolve token expiration issue
docs(api): update authentication endpoints
test(coordinator): add approval workflow tests
refactor(database): optimize query performance
```

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues
Closes #123
Related to #456

## Testing
Describe the tests you ran and how to reproduce them:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Browser testing (Chrome, Firefox, Safari)
- [ ] Mobile testing

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks pass
   - Security scans complete

2. **Peer Review**
   - At least one maintainer review required
   - Address feedback and comments
   - Request re-review after changes

3. **Final Approval**
   - All checks pass
   - Approved by maintainer
   - Ready for merge

### Merge Strategy

- **Feature branches**: Squash and merge
- **Hotfixes**: Merge commit
- **Documentation**: Squash and merge

---

## 🐛 Issue Reporting

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Check documentation** for known solutions
3. **Test with latest version** to ensure issue persists
4. **Gather system information** for context

### Issue Template

#### Bug Report
```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Python Version: [e.g. 3.11.0]
- Node Version: [e.g. 18.0.0]

**Additional Context**
Add any other context about the problem here.
```

#### Feature Request
```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on
- `priority-high`: High priority issue
- `priority-medium`: Medium priority issue
- `priority-low`: Low priority issue

---

## 📚 Documentation

### Documentation Standards

#### Code Documentation
- **Functions**: Include docstrings with parameters, return values, and examples
- **Classes**: Document purpose, attributes, and usage
- **Complex Logic**: Add inline comments explaining the approach
- **APIs**: Document all endpoints with examples

#### User Documentation
- **Step-by-step guides** with screenshots
- **Code examples** that can be copy-pasted
- **Common use cases** and scenarios
- **Troubleshooting sections** for known issues

#### API Documentation
- **Endpoint descriptions** with purpose and behavior
- **Request/response examples** with all fields
- **Error codes** and their meanings
- **Authentication requirements**

### Documentation Structure

```
docs/
├── README.md                 # Project overview
├── INSTALLATION.md           # Setup instructions
├── API_REFERENCE.md          # Complete API documentation
├── USER_GUIDE.md            # End-user documentation
├── CONTRIBUTING.md          # This file
├── DEPLOYMENT.md            # Production deployment
├── ENVIRONMENT_VARIABLES.md # Configuration guide
├── CHANGELOG.md             # Version history
└── examples/                # Code examples
    ├── api_usage/
    ├── deployment/
    └── integration/
```

### Writing Guidelines

#### Style
- Use clear, concise language
- Write in present tense
- Use active voice when possible
- Include code examples for technical concepts

#### Format
- Use proper Markdown formatting
- Include table of contents for long documents
- Use consistent heading levels
- Add appropriate code syntax highlighting

#### Review Process
- Documentation changes require review
- Test all code examples
- Verify links work correctly
- Check for spelling and grammar

---

## 🏆 Recognition

### Contributors

We recognize contributions in multiple ways:

- **Contributors list** in README
- **Changelog mentions** for significant contributions
- **GitHub Discussions** highlighting great contributions
- **Special recognition** for first-time contributors

### Contributor Levels

#### First-Time Contributor
- Made first accepted contribution
- Added to contributors list
- Welcome message and guidance

#### Regular Contributor
- Multiple accepted contributions
- Invited to contributor discussions
- Can be assigned to issues

#### Core Contributor
- Significant ongoing contributions
- Trusted with review responsibilities
- Input on project direction

#### Maintainer
- Full repository access
- Final review authority
- Project governance participation

---

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community
- **Discord/Slack**: Real-time chat (if available)
- **Email**: Direct contact for sensitive issues

### Response Times

- **Bug reports**: 2-3 business days
- **Feature requests**: 1 week
- **Security issues**: 24 hours
- **General questions**: 3-5 business days

### Office Hours

Weekly virtual office hours for contributors:
- **Time**: Fridays 2-3 PM UTC
- **Format**: Video call with screen sharing
- **Topics**: Code review, architecture discussions, Q&A

---

## 📄 License

By contributing to AnnaiCONNECT, you agree that your contributions will be licensed under the same license as the project.

---

## 🙏 Thank You

Thank you for taking the time to contribute to AnnaiCONNECT! Your efforts help make this project better for everyone. Whether you're fixing bugs, adding features, improving documentation, or helping other users, every contribution is valuable and appreciated.

For questions about contributing, please create an issue or reach out to the maintainers.

**Happy contributing!** 🚀