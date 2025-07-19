# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

1. **Do NOT** open a public issue
2. Email us at <security@miktos.com> with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

3. We will respond within 48 hours
4. We will provide regular updates on our progress
5. We will credit you in our security acknowledgments (unless you prefer to remain anonymous)

## Security Features

- JWT-based authentication with secure token handling
- Rate limiting to prevent abuse
- Input validation and sanitization
- CORS protection for cross-origin requests
- Secure headers and HTTPS enforcement
- Environment variable protection
- No sensitive data logging
- Regular dependency security updates

## Security Best Practices

### For Developers

- Never commit secrets or API keys
- Use environment variables for sensitive configuration
- Validate all input data using Pydantic models
- Implement proper error handling without exposing internals
- Use secure coding practices for async operations
- Regular dependency updates and security scanning

### For Users

- Keep the application updated to the latest version
- Use strong, unique passwords for any integrations
- Secure your environment variables and configuration files
- Monitor logs for unusual activity
- Use HTTPS in production environments
- Be cautious when using custom models or workflows from untrusted sources

## Vulnerability Response Process

1. **Assessment**: We evaluate the severity and impact
2. **Confirmation**: We reproduce and confirm the vulnerability
3. **Development**: We develop and test a fix
4. **Release**: We release a security patch
5. **Disclosure**: We coordinate responsible disclosure

## Security Contacts

For security-related questions or concerns:

- Security Team: <security@miktos.com>
- GPG Key: Available upon request

Thank you for helping keep Miktos secure!
