# Development Rules

## Code Standards

1. **No Emojis**: Code must not contain any emoji characters
2. **No Useless Comments**: Only add comments where absolutely necessary to clarify complex logic
3. **Professional Tone**: All documentation and code must maintain a technical, professional tone
4. **Clean Code**: Code should be self-documenting; avoid redundant comments

## Shell Scripts

1. **Avoid New Shell Scripts**: Do not create new shell scripts unless absolutely necessary
2. **Existing Scripts**: Root-level shell scripts (`setup.sh`, `start.sh`, `launcher.py`) are acceptable as they provide user convenience
3. **Integrate Features**: Functionality should be integrated into the main application rather than added as standalone shell scripts

## Security Standards

**Context**: Epifania is a local security research tool that requires privileged access to perform dynamic analysis. It runs locally, connects to devices via ADB, and requires root access for instrumentation. Users are expected to understand the security implications.

1. **Input Validation**: Always validate and sanitize external inputs (device data, file paths, user-provided scripts)
2. **Dependencies**: Keep dependencies updated; review security advisories regularly
3. **Secrets Management**: Never hardcode credentials; use environment variables for API keys (e.g., GitHub tokens)
4. **Defense in Depth**: Validate data at API boundaries and before executing system commands
5. **Execution Context**: Document when operations require root access; fail gracefully when unavailable
6. **Error Handling**: Avoid exposing sensitive device information or internal paths in error messages; provide clear, actionable errors without leaking system details
7. **Command Injection**: Sanitize all inputs before passing to subprocess/shell commands (ADB, Frida)

## Comment Guidelines

- Do NOT comment obvious code
- Do NOT use decorative comments
- DO comment complex algorithms or non-obvious logic
- Keep comments short and technical

## Examples

BAD:
```python
# This function adds two numbers together
def add(a, b):
    return a + b  # Return the sum
```

GOOD:
```python
def add(a, b):
    return a + b
```

ACCEPTABLE:
```python
def calculate_needle_position(image, threshold):
    # Exponential backoff prevents API rate limiting
    time.sleep(2 ** attempt)
```
