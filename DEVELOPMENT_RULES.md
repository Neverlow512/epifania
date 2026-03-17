# Development Rules

## Code Standards

1. **No Emojis**: Code must not contain any emoji characters
2. **No Useless Comments**: Only add comments where absolutely necessary to clarify complex logic
3. **Professional Tone**: All documentation and code must maintain a technical, professional tone
4. **Clean Code**: Code should be self-documenting; avoid redundant comments
5. **Imports at the top**: Always place imports at the top of the file, unless the programming language requires them to be within functions.

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

---

## Frida Instrumentation

**CRITICAL**: All Frida hooks, attachments, and instrumentation logic must be implemented as JavaScript or TypeScript scripts stored in `backend/device/workshop_tab/script_vault/`, NOT as inline strings in Python code.

### Rules

1. **Script Storage**: All Frida scripts live in `script_vault/`, organized by category (discovery/, hooking/, tracing/)
2. **Language Selection**:
   - Use **JavaScript (`.js`)** for simple Frida scripts that use only the core Frida API
   - Use **TypeScript (`.ts`)** when you need native bridges (e.g., `frida-java-bridge`) or type safety
3. **Python Role**: Python code only loads and executes scripts via `script_loader.py` (for `.js`) or `script_compiler.py` (for `.ts`)
4. **No Inline Scripts**: Never embed Frida JavaScript code as strings in Python files
5. **Template Variables**: Use `{{VARIABLE_NAME}}` placeholders in scripts for dynamic values injected by Python

### Benefits

- **CodeShare Integration**: Easier to integrate community scripts from Frida CodeShare
- **Reusability**: Scripts can be reused across different parts of the application
- **Maintainability**: JavaScript/TypeScript tooling (linting, formatting, debugging) works properly
- **Organization**: Clear separation between orchestration (Python) and instrumentation (JS/TS)
- **Testing**: Scripts can be tested independently with Frida CLI tools

### Example

**BAD** (inline script in Python):
```python
script_code = """
Java.perform(function() {
    var Activity = Java.use('android.app.Activity');
    Activity.onCreate.implementation = function() {
        console.log('Activity created');
        this.onCreate.apply(this, arguments);
    };
});
"""
session.create_script(script_code)
```

**GOOD** (script in vault):
```javascript
// script_vault/hooking/trace_activity.js
Java.perform(function() {
    var Activity = Java.use('android.app.Activity');
    Activity.onCreate.implementation = function() {
        console.log('Activity created');
        this.onCreate.apply(this, arguments);
    };
});
```

```python
# Python code
from backend.device.workshop_tab.discovery.script_loader import script_loader
script_code = script_loader.load_script('hooking', 'trace_activity.js')
session.create_script(script_code)
```
---

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