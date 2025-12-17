import os
import re

def add_typing_import(filepath):
    """Add typing imports to a Python file if needed"""
    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Check what typing imports are needed
    imports_needed = []
    
    # Patterns to check
    patterns = {
        'Optional': r'\bOptional\[',
        'List': r'\bList\[',
        'Dict': r'\bDict\[',
        'Any': r'\bAny\b',
        'Tuple': r'\bTuple\[',
        'Union': r'\bUnion\[',
        'Type': r'\bType\[',
    }
    
    # Check for typing usage
    for type_name, pattern in patterns.items():
        if re.search(pattern, content):
            imports_needed.append(type_name)
    
    # Also check for type annotations without brackets
    if '-> Optional[' in content and 'Optional' not in imports_needed:
        imports_needed.append('Optional')
    
    # Remove duplicates and sort
    imports_needed = sorted(list(set(imports_needed)))
    
    if not imports_needed:
        return False
    
    # Check if typing import already exists
    typing_import_pattern = r'from typing import.*'
    typing_imports = []
    
    for i, line in enumerate(lines):
        if line.strip().startswith('from typing import'):
            # Extract existing imports
            match = re.match(r'from typing import (.*)', line.strip())
            if match:
                existing = [imp.strip() for imp in match.group(1).split(',')]
                typing_imports = existing
                # Add missing imports to existing line
                for imp in imports_needed:
                    if imp not in existing:
                        existing.append(imp)
                # Update the line
                lines[i] = f"from typing import {', '.join(sorted(existing))}"
                with open(filepath, 'w') as f:
                    f.write('\n'.join(lines))
                print(f"✓ Updated imports in {filepath}: added {imports_needed}")
                return True
    
    # No existing typing import, add a new one
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            # Insert before first import
            lines.insert(i, f"from typing import {', '.join(imports_needed)}")
            with open(filepath, 'w') as f:
                f.write('\n'.join(lines))
            print(f"✓ Added imports to {filepath}: {imports_needed}")
            return True
    
    # No imports at all, add at the top
    lines.insert(0, f"from typing import {', '.join(imports_needed)}")
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    print(f"✓ Added imports to {filepath}: {imports_needed}")
    return True

# Files that need fixing
files_to_fix = [
    "app/services/otp_service.py",
    "app/repositories/base_repository.py",
    "app/repositories/user_repository.py",
    "app/repositories/otp_repository.py",
    "app/schemas/common.py",
    "app/schemas/request/auth.py",
    "app/schemas/response/auth.py",
    "app/schemas/response/user.py",
    "app/core/security.py"
]

print("Fixing imports...")
for filepath in files_to_fix:
    if os.path.exists(filepath):
        add_typing_import(filepath)
    else:
        print(f"✗ File not found: {filepath}")

print("\nDone fixing imports!")