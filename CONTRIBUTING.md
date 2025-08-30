# Contributing to BHIV-Integrated Gurukul Content Platform

Thank you for your interest in contributing to the BHIV platform! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/gurukul-content-platform.git
   cd gurukul-content-platform
   ```
3. **Set up development environment**
   ```bash
   make dev
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
4. **Run tests**
   ```bash
   make test
   ```

## 🏗️ Development Workflow

### Branch Naming
- `feat/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/update-description` - Documentation updates
- `refactor/component-name` - Code refactoring

### Code Standards
- **Python**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type hints for all functions
- **Documentation**: Document all public functions and classes
- **Testing**: Write tests for new features

### Before Submitting
```bash
make format  # Format code
make lint    # Check linting
make test    # Run tests
```

## 🧪 Testing

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_bhiv_core.py

# With coverage
pytest --cov=. --cov-report=html
```

### Test Structure
- `tests/test_*.py` - Unit tests
- `tests/integration/` - Integration tests
- `smoke_test.py` - End-to-end tests

## 📝 Pull Request Process

1. **Create feature branch** from `develop`
2. **Make changes** following code standards
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Submit pull request** with clear description

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## 🏛️ Architecture Guidelines

### BHIV Components
- **Bucket**: File storage and metadata management
- **Human-in-the-loop**: User feedback collection
- **Intelligence**: AI-powered analysis and insights
- **Video**: Video generation and processing

### Code Organization
```
├── backend/           # FastAPI server
├── video/            # Video processing
├── analytics/        # Analytics and feedback
├── security/         # Authentication and security
├── tests/           # Test suite
└── frontend/        # User interface
```

## 🔒 Security Guidelines

- **Never commit secrets** or API keys
- **Validate all inputs** from users
- **Use parameterized queries** for database operations
- **Follow OWASP guidelines** for web security
- **Test security features** thoroughly

## 📚 Documentation

### Code Documentation
- Use docstrings for all functions and classes
- Include type hints
- Document complex algorithms
- Add inline comments for clarity

### API Documentation
- Update OpenAPI schemas for new endpoints
- Include request/response examples
- Document error codes and messages

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Test with latest version
3. Gather system information

### Bug Report Template
```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce the behavior

**Expected behavior**
What you expected to happen

**Environment**
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.9]
- Platform version: [e.g., 2.0.0]

**Additional context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
Description of the problem

**Describe the solution you'd like**
Clear description of desired feature

**Describe alternatives you've considered**
Alternative solutions considered

**Additional context**
Any other relevant information
```

## 🎯 Areas for Contribution

### High Priority
- Performance optimizations
- Additional video formats
- Enhanced analytics
- Mobile responsiveness

### Medium Priority
- Additional authentication providers
- Batch processing
- API rate limiting
- Monitoring dashboards

### Good First Issues
- Documentation improvements
- Test coverage
- Code formatting
- Minor bug fixes

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: team@bhiv.platform for security issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the BHIV platform! 🚀