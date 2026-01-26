# Validate Extension Submission Skill

Automatically validate that an extension meets all requirements for Extension Index submission.

## When to Use

Use this skill when:
- Ready to verify extension meets submission requirements
- Before creating a pull request to ExtensionsIndex
- After making changes to ensure nothing is broken

## CRITICAL: Fetch Latest Requirements First

**This skill MUST fetch and verify against the latest official requirements before validating:**

```bash
# 1. Fetch current PR template (authoritative checklist)
curl -s "https://raw.githubusercontent.com/Slicer/ExtensionsIndex/main/.github/PULL_REQUEST_TEMPLATE.md" > /tmp/slicer_pr_template.md

# 2. Fetch current JSON schema
curl -s "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json" > /tmp/slicer_schema.json

# 3. Check schema version in fetched file
cat /tmp/slicer_schema.json | grep -o '"$id"[^,]*'
```

If the schema version has changed from `v1.0.1`, **STOP and notify the user** that requirements may have changed.

---

## Validation Steps

### Step 1: Verify Latest Requirements Retrieved

```bash
# Confirm PR template was fetched
if [ -s /tmp/slicer_pr_template.md ]; then
  echo "PR template fetched successfully"
  head -5 /tmp/slicer_pr_template.md
else
  echo "ERROR: Failed to fetch PR template"
fi

# Confirm schema was fetched
if [ -s /tmp/slicer_schema.json ]; then
  echo "Schema fetched successfully"
  cat /tmp/slicer_schema.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Schema version: {d.get(\"\$id\", \"unknown\")}')"
else
  echo "ERROR: Failed to fetch schema"
fi
```

---

### Step 2: Repository Structure Validation

```bash
# Check required files exist
echo "=== Repository Structure ==="
[ -f CMakeLists.txt ] && echo "[PASS] CMakeLists.txt exists" || echo "[FAIL] CMakeLists.txt missing"
[ -f LICENSE.txt ] || [ -f LICENSE ] && echo "[PASS] LICENSE file exists" || echo "[FAIL] LICENSE file missing"
[ -f README.md ] && echo "[PASS] README.md exists" || echo "[FAIL] README.md missing"

# Check for icon file
ICON_FILES=$(find . -maxdepth 2 -name "*.png" -type f 2>/dev/null | head -5)
[ -n "$ICON_FILES" ] && echo "[PASS] PNG files found: $ICON_FILES" || echo "[WARN] No PNG files found for icon"
```

---

### Step 3: CMakeLists.txt Metadata Validation

```bash
echo "=== CMakeLists.txt Metadata ==="

# Extract metadata
HOMEPAGE=$(grep -oP 'EXTENSION_HOMEPAGE\s+"[^"]*"' CMakeLists.txt | cut -d'"' -f2)
CONTRIBUTORS=$(grep -oP 'EXTENSION_CONTRIBUTORS\s+"[^"]*"' CMakeLists.txt | cut -d'"' -f2)
DESCRIPTION=$(grep -oP 'EXTENSION_DESCRIPTION\s+"[^"]*"' CMakeLists.txt | cut -d'"' -f2)
ICONURL=$(grep -oP 'EXTENSION_ICONURL\s+"[^"]*"' CMakeLists.txt | cut -d'"' -f2)
SCREENSHOTURLS=$(grep -oP 'EXTENSION_SCREENSHOTURLS\s+"[^"]*"' CMakeLists.txt | cut -d'"' -f2)
DEPENDS=$(grep -oP 'EXTENSION_DEPENDS\s+"[^"]*"' CMakeLists.txt | cut -d'"' -f2)

# Validate each field
echo "HOMEPAGE: $HOMEPAGE"
[[ "$HOMEPAGE" != *"example.com"* ]] && echo "[PASS] Homepage not placeholder" || echo "[FAIL] Homepage is placeholder"

echo "CONTRIBUTORS: $CONTRIBUTORS"
[[ "$CONTRIBUTORS" != *"John Doe"* ]] && echo "[PASS] Contributors not placeholder" || echo "[FAIL] Contributors is placeholder"

echo "DESCRIPTION: $DESCRIPTION"
[[ "$DESCRIPTION" != *"example"* ]] && echo "[PASS] Description not placeholder" || echo "[FAIL] Description is placeholder"

echo "ICONURL: $ICONURL"
[[ "$ICONURL" == https://raw.githubusercontent.com/* ]] && echo "[PASS] Icon URL is raw GitHub" || echo "[FAIL] Icon URL should be raw.githubusercontent.com"

echo "SCREENSHOTURLS: $SCREENSHOTURLS"
[[ "$SCREENSHOTURLS" == https://raw.githubusercontent.com/* ]] && echo "[PASS] Screenshot URL is raw GitHub" || echo "[FAIL] Screenshot URL should be raw.githubusercontent.com"

echo "DEPENDS: $DEPENDS"
```

---

### Step 4: URL Accessibility Validation

```bash
echo "=== URL Accessibility ==="

# Test homepage
if [ -n "$HOMEPAGE" ]; then
  HTTP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$HOMEPAGE" 2>/dev/null)
  [ "$HTTP_CODE" = "200" ] && echo "[PASS] Homepage accessible (HTTP $HTTP_CODE)" || echo "[FAIL] Homepage returned HTTP $HTTP_CODE"
fi

# Test icon URL
if [ -n "$ICONURL" ]; then
  HTTP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$ICONURL" 2>/dev/null)
  [ "$HTTP_CODE" = "200" ] && echo "[PASS] Icon URL accessible (HTTP $HTTP_CODE)" || echo "[FAIL] Icon URL returned HTTP $HTTP_CODE"
fi

# Test screenshot URLs (first one)
if [ -n "$SCREENSHOTURLS" ]; then
  FIRST_SCREENSHOT=$(echo "$SCREENSHOTURLS" | awk '{print $1}')
  HTTP_CODE=$(curl -sI -o /dev/null -w "%{http_code}" "$FIRST_SCREENSHOT" 2>/dev/null)
  [ "$HTTP_CODE" = "200" ] && echo "[PASS] Screenshot URL accessible (HTTP $HTTP_CODE)" || echo "[FAIL] Screenshot URL returned HTTP $HTTP_CODE"
fi
```

---

### Step 5: Extension Index JSON Validation

If a JSON file exists for submission:

```bash
echo "=== Extension Index JSON Validation ==="

JSON_FILE=$(find . -maxdepth 1 -name "*.json" -type f | grep -v package | head -1)

if [ -n "$JSON_FILE" ]; then
  echo "Found: $JSON_FILE"

  # Validate JSON syntax
  python3 -c "import json; json.load(open('$JSON_FILE'))" 2>&1 && echo "[PASS] Valid JSON syntax" || echo "[FAIL] Invalid JSON syntax"

  # Validate against schema
  python3 << EOF
import json

with open('$JSON_FILE') as f:
    data = json.load(f)

required = ['\$schema', 'category', 'scm_url']
for field in required:
    if field in data:
        print(f"[PASS] Required field '{field}' present")
    else:
        print(f"[FAIL] Required field '{field}' missing")

# Check schema URL
if data.get('\$schema', '').startswith('https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/'):
    print("[PASS] Schema URL is official Slicer schema")
else:
    print("[FAIL] Schema URL should reference official Slicer schema")

# Check scm_url format
if data.get('scm_url', '').endswith('.git'):
    print("[PASS] scm_url ends with .git")
else:
    print("[WARN] scm_url should end with .git")

# Check tier
tier = data.get('tier', 1)
print(f"[INFO] Extension tier: {tier}")
EOF

else
  echo "[WARN] No Extension Index JSON file found in current directory"
  echo "       Run /prepare-extension-metadata to generate one"
fi
```

---

### Step 6: GitHub Repository Settings Check

```bash
echo "=== GitHub Repository Checks ==="

# Extract repo from scm_url or HOMEPAGE
REPO_URL=$(grep -oP 'https://github.com/[^/]+/[^/\s"#]+' CMakeLists.txt | head -1)

if [ -n "$REPO_URL" ]; then
  REPO_PATH=$(echo "$REPO_URL" | sed 's|https://github.com/||' | sed 's|\.git$||' | sed 's|#.*||')
  echo "Repository: $REPO_PATH"

  # Check for 3d-slicer-extension topic (requires gh CLI)
  if command -v gh &> /dev/null; then
    TOPICS=$(gh repo view "$REPO_PATH" --json repositoryTopics -q '.repositoryTopics[].name' 2>/dev/null)
    if echo "$TOPICS" | grep -q "3d-slicer-extension"; then
      echo "[PASS] Repository has '3d-slicer-extension' topic"
    else
      echo "[FAIL] Repository missing '3d-slicer-extension' topic"
      echo "       Add via: GitHub repo Settings > About > Topics"
    fi
  else
    echo "[SKIP] gh CLI not available - manually verify '3d-slicer-extension' topic"
  fi
else
  echo "[WARN] Could not determine repository URL"
fi
```

---

### Step 7: License Validation

```bash
echo "=== License Validation ==="

LICENSE_FILE=""
[ -f LICENSE.txt ] && LICENSE_FILE="LICENSE.txt"
[ -f LICENSE ] && LICENSE_FILE="LICENSE"
[ -f LICENSE.md ] && LICENSE_FILE="LICENSE.md"

if [ -n "$LICENSE_FILE" ]; then
  echo "License file: $LICENSE_FILE"

  # Check for common permissive licenses
  if grep -qi "MIT License\|MIT license" "$LICENSE_FILE"; then
    echo "[PASS] MIT License detected (recommended)"
  elif grep -qi "Apache License" "$LICENSE_FILE"; then
    echo "[PASS] Apache License detected (recommended)"
  elif grep -qi "BSD" "$LICENSE_FILE"; then
    echo "[PASS] BSD License detected (acceptable)"
  elif grep -qi "GPL\|GNU General Public" "$LICENSE_FILE"; then
    echo "[WARN] GPL License detected - document reason in extension description"
  else
    echo "[INFO] License type not auto-detected - verify manually"
  fi
else
  echo "[FAIL] No LICENSE file found"
fi
```

---

### Step 8: README/Homepage Content Validation

```bash
echo "=== README Content Validation ==="

if [ -f README.md ]; then
  # Check for required homepage content
  grep -qi "installation\|install" README.md && echo "[PASS] Installation section found" || echo "[WARN] Installation section not found"
  grep -qi "usage\|how to\|getting started" README.md && echo "[PASS] Usage section found" || echo "[WARN] Usage section not found"

  # Check for images
  if grep -qE "!\[.*\]\(.*\.(png|jpg|gif)" README.md; then
    echo "[PASS] Images found in README"
  else
    echo "[WARN] No images found in README - at least one recommended"
  fi

  # Check description length (first paragraph approximation)
  FIRST_PARA=$(sed -n '/^[^#]/p' README.md | head -5)
  echo "[INFO] First paragraph preview:"
  echo "$FIRST_PARA" | head -3
else
  echo "[FAIL] README.md not found"
fi
```

---

## Validation Summary Output

After all checks, provide a summary:

```
=== VALIDATION SUMMARY ===

Tier 1 Requirements:
  [ ] Extension name appropriate
  [ ] Repository naming convention
  [ ] 3d-slicer-extension topic
  [ ] Description (1-2 sentences)
  [ ] LICENSE file present
  [ ] All URLs accessible
  [ ] JSON file valid
  [ ] Homepage has required content

Ready for Tier 1 submission: YES/NO

Next steps:
  1. Fix any [FAIL] items above
  2. Run /extension-submission-checklist for full checklist
  3. Run /prepare-extension-metadata to generate JSON file
  4. Submit PR to https://github.com/Slicer/ExtensionsIndex
```

---

## Automated Full Validation Script

Run all validations in sequence:

```bash
#!/bin/bash
set -e

echo "============================================"
echo "Slicer Extension Submission Validator"
echo "============================================"
echo ""
echo "Fetching latest requirements..."

# Fetch latest requirements
curl -s "https://raw.githubusercontent.com/Slicer/ExtensionsIndex/main/.github/PULL_REQUEST_TEMPLATE.md" > /tmp/slicer_pr_template.md
curl -s "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json" > /tmp/slicer_schema.json

echo "Requirements fetched. Running validation..."
echo ""

# Run all validation steps (paste steps 2-8 here)

echo ""
echo "Validation complete."
```

## Notes

- All validation against **fetched** requirements, not cached versions
- If schema version changes, this skill should be updated
- Some checks require `gh` CLI for GitHub API access
- Manual verification still required for some Tier 3/5 requirements
