#!/usr/bin/env python3
"""Test the actual response format that's causing the error"""

# Simulate the actual response from the debug file
text = """```json
{
  "date": "2025-10-29",
  "bias": "neutral_observation"
}
```%"""

print("Original text:")
print(repr(text))
print("\n" + "="*60 + "\n")

# Test the splitting logic
parts = text.split("```")
print(f"Number of parts after split: {len(parts)}")
for i, part in enumerate(parts):
    print(f"Part {i}: {repr(part[:50])}{'...' if len(part) > 50 else ''}")

print("\n" + "="*60 + "\n")

# Test our logic
plan_text = text.strip()

if plan_text.startswith("```"):
    parts = plan_text.split("```")
    print(f"Split produced {len(parts)} parts")
    
    if len(parts) >= 3:
        print("Using parts[1] (len >= 3)")
        plan_text = parts[1].strip()
    elif len(parts) >= 2:
        print("Using parts[1] (len >= 2)")
        plan_text = parts[1].strip()
    else:
        print("Removing first 3 chars")
        plan_text = plan_text[3:].strip()
    
    # Remove language identifier
    if plan_text.startswith("json"):
        plan_text = plan_text[4:].strip()
    elif plan_text.startswith("JSON"):
        plan_text = plan_text[4:].strip()

# Remove trailing ```
if plan_text.endswith("```"):
    plan_text = plan_text[:-3].strip()

print("\nFinal cleaned text:")
print(plan_text)
print("\n" + "="*60)

# Try to parse
import json
try:
    result = json.loads(plan_text)
    print("\n✅ Successfully parsed!")
    print(result)
except Exception as e:
    print(f"\n❌ Failed to parse: {e}")
