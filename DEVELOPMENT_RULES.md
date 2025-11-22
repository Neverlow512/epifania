# Development Rules

## Code Standards

1. **No Emojis**: Code must not contain any emoji characters
2. **No Useless Comments**: Only add comments where absolutely necessary to clarify complex logic
3. **Professional Tone**: All documentation and code must maintain a technical, professional tone
4. **Clean Code**: Code should be self-documenting; avoid redundant comments

## Comment Guidelines

- Do NOT comment obvious code
- Do NOT use decorative comments
- DO comment complex algorithms or non-obvious logic
- Keep comments short and technical

## Security Standards

1. **Input Validation**: Always validate and sanitize external inputs
2. **Dependencies**: Keep dependencies updated; review security advisories regularly
3. **Secrets Management**: Never hardcode credentials; use environment variables or secure vaults
4. **Defense in Depth**: Implement multiple layers of security controls
5. **Least Privilege**: Grant minimum necessary permissions to users and processes
6. **Error Handling**: Avoid exposing sensitive information in error messages

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
