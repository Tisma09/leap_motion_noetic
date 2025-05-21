import re

##############################################################################
## For clean the errors after swig generation
## Some error must be correct manually even after this scripts
##############################################################################


INPUT_FILE = "Leap.py"
OUTPUT_FILE = "Leap_cleaned.py"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    code = f.read()

# Remove annotations
code = re.sub(r'->\s*"[^"]*"', '', code)
code = re.sub(r'(\w+)\s*:\s*["\'][^"\']*["\']', r'\1', code)

# Clean parentheses after remove annotations
code = re.sub(r'\(\s*,', '(', code)  # corect virgules at start
code = re.sub(r',\s*\)', ')', code)  # ccorect virgules at end

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(code)

print(f"Annotations cleaned. New file : {OUTPUT_FILE}")
