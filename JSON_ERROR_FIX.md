# JSON Parsing Error Fix

## Problem
The GitHub Actions workflow was failing with the error:
```
Error generating plan: Unterminated string starting at: line 13 column 3 (char 210)
```

This is a `JSONDecodeError` that occurs when the Gemini AI model returns malformed JSON that Python's `json.loads()` cannot parse.

## Root Cause
The error occurred in `gemex/ace/components.py` in the `run_generator()` function. The code was:
1. Requesting JSON output from the Gemini AI model
2. Attempting basic cleanup of markdown formatting
3. Parsing the response with `json.loads()`

However, the AI model sometimes returns:
- Incomplete JSON strings
- Improperly escaped characters
- Nested markdown code blocks
- Extra trailing characters

The original error handling caught all exceptions generically, making it difficult to debug what went wrong.

## Solution Implemented

### 1. **Debug Logging**
Added automatic saving of raw AI responses to a debug folder:
```python
debug_dir = Path("trading_session") / "debug"
debug_file = debug_dir / f"raw_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
```

This allows inspection of the actual malformed JSON that caused the error.

### 2. **Improved JSON Cleaning**
Enhanced the markdown stripping logic to handle more edge cases:
```python
# Better handling of markdown code blocks
if plan_text.startswith("```"):
    parts = plan_text.split("```")
    if len(parts) >= 2:
        plan_text = parts[1]
        # Handle both "json" and "JSON" identifiers
        if plan_text.strip().startswith("json"):
            plan_text = plan_text.strip()[4:].strip()
        elif plan_text.strip().startswith("JSON"):
            plan_text = plan_text.strip()[4:].strip()

# Remove trailing markdown markers
if plan_text.endswith("```"):
    plan_text = plan_text[:-3].strip()
```

### 3. **Specific JSON Error Handling**
Separated `JSONDecodeError` from general exceptions:
```python
try:
    plan = json.loads(plan_text)
except json.JSONDecodeError as json_err:
    print(f"❌ JSON parsing failed: {json_err}")
    print(f"📄 First 500 chars of response: {plan_text[:500]}")
    print(f"📄 Last 200 chars of response: {plan_text[-200:]}")
    raise  # Re-raise to be caught by outer handler
```

This provides detailed diagnostic output in the GitHub Actions logs.

### 4. **Graceful Degradation**
Returns a neutral trading plan when JSON parsing fails:
```python
return {
    "date": datetime.now().strftime("%Y-%m-%d"),
    "bias": "neutral",
    "rationale": f"JSON parsing error: {str(e)}. The AI response was malformed.",
    "confidence": "low",
    "playbook_bullets_used": [],
    "error": f"JSONDecodeError: {str(e)}"
}
```

This ensures the workflow continues rather than crashing completely.

### 5. **Applied to Both Components**
The same fix was applied to:
- `run_generator()` - Daily trading plan generation
- `run_reflector()` - Weekly performance reflection

## Files Modified
- `gemex/ace/components.py` - Enhanced JSON parsing in both `run_generator()` and `run_reflector()`

## Testing Recommendations

### Local Testing
```bash
# Activate virtual environment
source gemx_venv/bin/activate

# Run a daily cycle to test the fix
python gemex/ace/main.py --cycle daily

# Check debug output if there are issues
ls -la trading_session/debug/
cat trading_session/debug/raw_response_*.txt
```

### GitHub Actions Testing
1. Trigger the workflow manually via "Run workflow" button
2. Select "daily" cycle
3. Monitor the logs for:
   - ✅ Success: Trading plan generated normally
   - 📝 Debug logs: Raw response saved to debug folder
   - ⚠️  Neutral plan: Graceful fallback if JSON parsing fails

### What to Look For
- The workflow should **not crash** even if Gemini returns bad JSON
- Debug files should be created in `trading_session/debug/` when errors occur
- Error messages should include snippets of the problematic JSON
- The system should continue with a neutral trading plan

## Prevention Strategies

### 1. Prompt Engineering
The system prompts already request "strict JSON format", but could be enhanced:
```python
user_prompt = f"""
...
Provide your analysis in VALID JSON format only. No markdown, no code blocks, just pure JSON.
Start with {{ and end with }}. Ensure all strings are properly escaped.
"""
```

### 2. JSON Schema Validation
Consider adding pydantic or jsonschema validation:
```python
from jsonschema import validate, ValidationError

# Define expected schema
trading_plan_schema = {
    "type": "object",
    "required": ["date", "bias", "confidence", "rationale"],
    "properties": {
        "date": {"type": "string"},
        "bias": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "rationale": {"type": "string"}
    }
}

# Validate before use
validate(instance=plan, schema=trading_plan_schema)
```

### 3. Retry Logic
Add retry mechanism with exponential backoff:
```python
MAX_RETRIES = 3
for attempt in range(MAX_RETRIES):
    try:
        plan = json.loads(plan_text)
        break
    except JSONDecodeError:
        if attempt < MAX_RETRIES - 1:
            print(f"Retry {attempt + 1}/{MAX_RETRIES}...")
            # Regenerate with adjusted prompt
        else:
            # Fall back to neutral plan
```

## Monitoring
After deployment, monitor:
1. **Debug folder growth** - Indicates how often JSON parsing fails
2. **Neutral plan frequency** - Shows fallback rate
3. **GitHub Actions logs** - Review error snippets to identify patterns

## Related Documentation
- `GITHUB_ACTIONS_ERROR_FIXES.md` - General GitHub Actions troubleshooting
- `TESTING_GUIDE.md` - How to test the ACE system
- `gemex/prompts.py` - System prompts for AI components
