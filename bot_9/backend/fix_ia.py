import re

with open('ia.py', 'r') as f:
    content = f.read()

# Add the history filtering logic
replacement = """    chat_history = []
    if history:
        for msg in history:
            role = msg.get("role")
            parts = [types.Part.from_text(text=p) for p in msg.get("parts", []) if p]
            if parts:
                chat_history.append(types.Content(role=role, parts=parts))

    valid_history = []
    expected_role = "user"
    for msg in chat_history:
        if msg.role == expected_role:
            valid_history.append(msg)
            expected_role = "model" if expected_role == "user" else "user"
            
    if valid_history and valid_history[-1].role == "user":
        valid_history.pop()
        
    chat_history = valid_history"""

content = re.sub(
    r'    chat_history = \[\]\n    if history:\n        for msg in history:\n            role = msg.get\("role"\)\n            parts = \[types.Part.from_text\(text=p\) for p in msg.get\("parts", \[\]\) if p\]\n            if parts:\n                chat_history.append\(types.Content\(role=role, parts=parts\)\)',
    replacement,
    content
)

with open('ia.py', 'w') as f:
    f.write(content)
