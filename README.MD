# AI Security Training Platform

An interactive educational platform for learning AI security vulnerabilities and defenses through hands-on practice with a simulated banking system.

## IMPORTANT SECURITY NOTICE

**This is an intentionally vulnerable application designed for educational purposes only.**

- Contains multiple security vulnerabilities by design
- Should NEVER be deployed in production
- Only run in isolated, controlled environments
- Used for cybersecurity education and AI safety research

## Overview

This platform demonstrates common AI security attacks and defense mechanisms through:

- **Vulnerable Banking API**: FastAPI backend with intentional security flaws
- **Interactive Frontend**: Streamlit-based attack and defense laboratories
- **LLM Integration**: Groq API integration using `openai/gpt-oss-120b`
- **Educational Content**: Comprehensive learning resources and case studies

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Streamlit UI      │    │    FastAPI Backend   │    │   SQLite DB     │
│  (Port 8501)        │───▶│    (Port 8000)       │───▶│  secure_bank.db │
│                     │    │                      │    │                 │
│ - Attack Lab        │    │ - Authentication     │    │ - User accounts │
│ - Defense Lab       │    │ - Banking API        │    │ - Transactions  │
│ - Learning Content  │    │ - AI Chat Endpoint   │    │ - System config │
└─────────────────────┘    └──────────────────────┘    └─────────────────┘
                                        │
                                        ▼
                           ┌──────────────────────┐
                           │     Groq API         │
                           │  (LLM Processing)    │
                           └──────────────────────┘
```

## Features

### Attack Laboratory
- **Prompt Injection**: Override system instructions
- **Function Abuse**: Exploit AI function calling
- **Information Disclosure**: Extract sensitive data
- **Context Manipulation**: Abuse conversation memory
- **Social Engineering**: Manipulate through false authority

### Defense Laboratory
- **Pattern Analysis**: Test defense mechanisms
- **Rule Configuration**: Customize security rules
- **Security Monitoring**: Real-time attack detection

### Educational Resources
- Attack type explanations and examples
- Defense strategy documentation
- Security best practices
- Real-world case studies

## Prerequisites

- Python 3.12 (lab target)
- Groq API key ([Get one here](https://console.groq.com/))
- 2GB+ RAM recommended
- Network access for API calls

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-security-training-platform
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```


## Usage

### 1. Start the Backend Server
```bash
python -m backend
```
The API will be available at `http://localhost:8000`

### 2. Start the Frontend (New Terminal)
```bash
python -m streamlit run app.py
```
The web interface will open at `http://localhost:8501`

### 3. Login with Demo Accounts

| Username | Password | Security Level | Description |
|----------|----------|----------------|-------------|
| `alice_johnson` | `SecurePass123!` | Level 1 | Standard user |
| `bob_smith` | `MyBankingPwd!` | Level 2 | Premium user |
| `charlie_admin` | `AdminSecure2024!` | Level 3 | Admin user |

### 4. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Create an account and generate an API key
3. Enter the key in the Attack Lab interface

The lab uses Groq's `openai/gpt-oss-120b` model with a 2,000-token completion limit.

## Inspect Server Traffic with Burp Suite

The lab can optionally send both server-side HTTP connections through Burp Suite:

```text
Streamlit -> Burp -> FastAPI
FastAPI -> Burp -> Groq
```

This mode is intended for a single-student Linux workstation where Burp, Streamlit,
and FastAPI all run on the same machine. It is opt-in. If the environment variables
below are not set, both applications retain their normal direct connections.

### 1. Start Burp

1. Start Burp Suite Community and create a temporary project.
2. Open the proxy settings and confirm that a listener is running on
   `127.0.0.1:8080`.
3. Turn **Intercept off** and use the **HTTP history** tab for observation. Leaving
   interception on pauses server requests and can trigger the application's
   ten-second timeout.

Burp's built-in browser is already configured for Burp. The environment variables
below are still required because Python server processes do not inherit the built-in
browser's proxy settings.

### 2. Export the Burp CA Certificate

In Burp's proxy settings, use **Import / export CA certificate**, select
**Certificate in DER format**, and save it as `burp-ca.der` in the project directory.
Convert it to PEM for Python:

```bash
openssl x509 -inform DER -in burp-ca.der -out burp-ca.pem
```

The application adds this certificate to normal system trust. TLS verification is
not disabled. The local `burp-ca.der` and `burp-ca.pem` files are ignored by Git.

### 3. Start the Backend Through Burp

In the backend terminal:

```bash
source .venv/bin/activate
export LAB_PROXY_URL="http://127.0.0.1:8080"
export LAB_PROXY_CA_CERT="$PWD/burp-ca.pem"
python -m backend
```

Both variables must be set before starting the process. The application exits with
a configuration error if only one is set, the URL is malformed, or the certificate
cannot be loaded.

### 4. Start Streamlit Through Burp

In a separate terminal, set the same variables:

```bash
source .venv/bin/activate
export LAB_PROXY_URL="http://127.0.0.1:8080"
export LAB_PROXY_CA_CERT="$PWD/burp-ca.pem"
python -m streamlit run app.py
```

Open `http://localhost:8501` using Burp's built-in browser. After logging in and
sending a chat message, Burp's HTTP history should contain:

- `POST http://localhost:8000/api/login`
- `POST http://localhost:8000/api/chat`
- An HTTPS request to `api.groq.com`, normally
  `/openai/v1/chat/completions`

The Groq request shows the authorization header, system prompt, conversation
history, model, and generation parameters. Use a dedicated, low-quota lab API key
and discard the temporary Burp project after the exercise. Burp cannot show SQLite
queries or Python function calls because those operations do not cross a network.

### Run Without Burp

Do not set the lab proxy variables, or remove them before starting both processes:

```bash
unset LAB_PROXY_URL LAB_PROXY_CA_CERT
python -m backend
```

Start Streamlit in another terminal without those variables. Burp does not need to
be running, and the application connects directly as it did before proxy support.

### Burp Troubleshooting

**Connection refused at `127.0.0.1:8080`:**
- Confirm Burp is running before both Python processes start.
- Confirm the proxy listener is bound to `127.0.0.1:8080`.

**Certificate verification failed for Groq:**
- Confirm `LAB_PROXY_CA_CERT` is an absolute path to the PEM file.
- Re-export the current Burp project CA and repeat the DER-to-PEM conversion.
- Restart the FastAPI backend after changing the environment.

**FastAPI requests do not appear in Burp:**
- Export both variables in the Streamlit terminal and restart Streamlit.
- Check HTTP history rather than only the Intercept tab.

**Groq requests do not appear in Burp:**
- Export both variables in the backend terminal and restart the backend.
- Check that `api.groq.com` is not configured for TLS pass-through in Burp.

**Requests time out while intercepting:**
- Turn Intercept off, or forward Streamlit-to-FastAPI requests within ten seconds.

## Intentional Vulnerabilities

This system contains the following educational vulnerabilities:

### Authentication & Authorization
- Weak password policies
- Admin bypass codes in system config
- Insufficient access controls
- Debug endpoints with minimal protection

### AI/LLM Specific
- Prompt injection susceptibility
- Function calling abuse
- Context manipulation vulnerabilities
- Insufficient input sanitization

### API Security
- Information disclosure through error messages
- User enumeration capabilities
- Direct SQL execution endpoints
- Insufficient rate limiting

### Data Protection
- Sensitive data exposure
- Weak encryption practices
- Inadequate data classification
- Audit log vulnerabilities

## Educational Objectives

Students will learn to:

1. **Identify Vulnerabilities**: Recognize AI security weaknesses
2. **Execute Attacks**: Practice exploitation techniques safely
3. **Implement Defenses**: Build security countermeasures
4. **Analyze Threats**: Understand attack patterns
5. **Monitor Systems**: Detect and respond to incidents

## File Structure

```
├── backend.py                  # Vulnerable backend API
├── app.py                      # Interactive frontend
├── requirements.txt            # Python 3.12 dependency pins
├── secure_bank.db              # SQLite database (auto-generated)
├── security_audit.log          # Security event logs
└── README.MD                   # This file
```

## API Endpoints

### Public Endpoints
- `POST /api/login` - User authentication
- `GET /api/health` - System health check

### Protected Endpoints
- `GET /api/account/{id}` - Account information
- `GET /api/transactions/{id}` - Transaction history
- `POST /api/transfer` - Money transfer
- `POST /api/chat` - AI assistant chat

### Admin/Debug Endpoints
- `GET /api/admin/users` - List all users (admin key required)
- `GET /api/system/config` - System configuration
- `POST /api/debug/sql` - Direct SQL execution (debug token required)
- `GET /api/search/users` - User search/enumeration

## Security Monitoring

The system logs all activities to `security_audit.log` including:
- Login attempts (successful and failed)
- API access patterns
- Anomaly scores for requests
- Function call executions
- Admin operations

## Troubleshooting

### Common Issues

**Cannot login with demo accounts:**
- Delete `secure_bank.db` and restart the backend
- Check that both servers are running

**Groq API errors:**
- Verify your API key is valid and has credits
- Check network connectivity
- Review rate limits on your Groq account

**Frontend connection errors:**
- Confirm backend is running on port 8000
- Check firewall settings
- Verify no port conflicts

**Database errors:**
- Delete `secure_bank.db` to reset
- Check file permissions
- Verify that the Python installation includes SQLite with `python -c "import sqlite3; print(sqlite3.sqlite_version)"`

### Reset Everything
```bash
# Stop both servers
# Delete the database
rm secure_bank.db
rm security_audit.log

# Restart the backend
python -m backend
```

## Educational Use Guidelines

### For Instructors
- Review all vulnerabilities before class
- Emphasize the educational nature
- Monitor student activities
- Provide guided exercises
- Discuss real-world implications

### For Students
- Only use in authorized environments
- Document your findings
- Practice both attack and defense
- Understand the underlying concepts
- Follow responsible disclosure principles

## Advanced Exercises

1. **Vulnerability Assessment**: Identify all security flaws
2. **Exploit Development**: Create custom attack payloads
3. **Defense Implementation**: Build additional security controls
4. **Monitoring Enhancement**: Improve detection capabilities
5. **Secure Redesign**: Architect a secure version

## Legal and Ethical Considerations

- Educational use only
- No real financial systems
- Respect others' systems and data
- Follow local laws and regulations
- Practice responsible disclosure

## Contributing

When contributing to this educational platform:
- Maintain the educational focus
- Document new vulnerabilities clearly
- Ensure changes don't break core functionality
- Add appropriate learning materials
- Follow security best practices for the educational content

## Support

For technical issues or educational questions:
1. Check the troubleshooting section
2. Review the learning resources
3. Consult security documentation
4. Contact the course instructor

## License

This educational platform is provided for cybersecurity training purposes. Use responsibly and in accordance with applicable laws and regulations.

---

**Remember: This is an intentionally vulnerable system for educational purposes only. Never deploy in production or use against systems you don't own.**
