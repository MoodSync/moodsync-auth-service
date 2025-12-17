import os
import re

def fix_pydantic_regex(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Replace regex= with pattern=
                new_content = re.sub(r'pattern="', 'pattern="', content)
                new_content = re.sub(r"pattern='", "pattern='", new_content)
                
                if new_content != content:
                    with open(filepath, 'w') as f:
                        f.write(new_content)
                    print(f"Fixed: {filepath}")

# Run the fix
fix_pydantic_regex('/home/psalms/my_workspace/backend_projects/MoodSync/moodsync-auth-service')