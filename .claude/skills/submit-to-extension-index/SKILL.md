---
name: Submit to Extension Index
description: Complete workflow for submitting an extension to the 3D Slicer Extension Index
allowed-tools:
  - WebFetch
  - Bash
  - Read
  - Write
  - Grep
context: manual
---

# Submit to Extension Index Skill

Complete workflow agent for submitting an extension to the 3D Slicer Extension Index.

## When to Use

Use this skill when:
- Ready to submit extension to the Slicer Extension Index
- Want guided walkthrough of entire submission process
- Need to create the pull request for submission

## CRITICAL: This Skill Fetches Live Requirements

This skill **always fetches the latest requirements** from official Slicer sources before proceeding. It will:

1. Fetch current PR template from ExtensionsIndex
2. Fetch current JSON schema from Slicer repository
3. Compare against known requirements
4. Alert if requirements have changed

**If requirements have changed, STOP and review changes before proceeding.**

---

## Pre-Submission Checklist (Verify Before Starting)

Before running this skill, ensure:

- [ ] Extension code is complete and tested
- [ ] Extension builds successfully in Slicer
- [ ] GitHub repository is public
- [ ] You have write access to the repository
- [ ] You have a GitHub account for PR submission

---

## Submission Workflow

### Phase 1: Fetch and Verify Latest Requirements

```bash
echo "=== Phase 1: Fetching Latest Official Requirements ==="

# Fetch PR template
PR_TEMPLATE=$(curl -sf "https://raw.githubusercontent.com/Slicer/ExtensionsIndex/main/.github/PULL_REQUEST_TEMPLATE.md")
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to fetch PR template. Check network connection."
  exit 1
fi
echo "[OK] PR template fetched"

# Fetch JSON schema
SCHEMA=$(curl -sf "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json")
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to fetch JSON schema. Check network connection."
  exit 1
fi
echo "[OK] JSON schema fetched"

# Extract and display schema version
SCHEMA_VERSION=$(echo "$SCHEMA" | python3 -c "import json,sys; print(json.load(sys.stdin).get('\$id','unknown'))")
echo "Schema version: $SCHEMA_VERSION"

# Check if schema version matches expected
if [[ "$SCHEMA_VERSION" != *"v1.0.1"* ]]; then
  echo ""
  echo "WARNING: Schema version may have changed!"
  echo "Expected: v1.0.1"
  echo "Found: $SCHEMA_VERSION"
  echo ""
  echo "Please review the new schema before continuing."
  echo "Fetch and review: curl -s '$SCHEMA_VERSION'"
fi
```

### Phase 2: Validate Extension Repository

Run `/validate-extension-submission` skill or execute:

```bash
echo "=== Phase 2: Validating Extension Repository ==="

# Check we're in the right directory
if [ ! -f CMakeLists.txt ]; then
  echo "ERROR: CMakeLists.txt not found. Run from extension root directory."
  exit 1
fi

# Run validation checks (abbreviated)
echo "Checking required files..."
[ -f LICENSE.txt ] || [ -f LICENSE ] || echo "FAIL: LICENSE file required"
[ -f README.md ] || echo "FAIL: README.md required"

echo "Checking CMakeLists.txt metadata..."
grep -q 'EXTENSION_HOMEPAGE' CMakeLists.txt || echo "FAIL: EXTENSION_HOMEPAGE required"
grep -q 'EXTENSION_CONTRIBUTORS' CMakeLists.txt || echo "FAIL: EXTENSION_CONTRIBUTORS required"
grep -q 'EXTENSION_DESCRIPTION' CMakeLists.txt || echo "FAIL: EXTENSION_DESCRIPTION required"
grep -q 'EXTENSION_ICONURL' CMakeLists.txt || echo "FAIL: EXTENSION_ICONURL required"

# Check for placeholder values
grep -q 'example.com' CMakeLists.txt && echo "FAIL: Placeholder URLs found in CMakeLists.txt"
grep -q 'John Doe' CMakeLists.txt && echo "FAIL: Placeholder contributor found in CMakeLists.txt"
```

### Phase 3: Update CMakeLists.txt Metadata

If placeholders found, update them:

```cmake
# Required metadata in CMakeLists.txt:

set(EXTENSION_HOMEPAGE "https://github.com/OWNER/REPO#readme")
set(EXTENSION_CONTRIBUTORS "Your Name (Your Affiliation)")
set(EXTENSION_DESCRIPTION "Brief 1-2 sentence description")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path/to/icon.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/OWNER/REPO/BRANCH/path/to/screenshot.png")
set(EXTENSION_DEPENDS "NA")
```

**For SlicerMouseMaster specifically:**

```cmake
set(EXTENSION_HOMEPAGE "https://github.com/benzwick/SlicerMouseMaster#readme")
set(EXTENSION_CONTRIBUTORS "Ben Zwick")
set(EXTENSION_DESCRIPTION "Advanced mouse customization with button remapping, workflow presets, and context-sensitive bindings for multi-button mice in 3D Slicer.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/SlicerMouseMaster/SlicerMouseMaster.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/benzwick/SlicerMouseMaster/main/Screenshots/main-ui.png")
set(EXTENSION_DEPENDS "NA")
```

### Phase 4: Generate Extension Index JSON File

Create the JSON file for ExtensionsIndex repository:

```bash
echo "=== Phase 4: Generating Extension Index JSON ==="

# Get extension name from CMakeLists.txt
EXT_NAME=$(grep -oP 'project\(\K[^)]+' CMakeLists.txt)
echo "Extension name: $EXT_NAME"

# Get repository URL (adjust as needed)
REPO_URL="https://github.com/OWNER/REPO.git"

# Generate JSON
cat > "${EXT_NAME}.json" << 'EOF'
{
  "$schema": "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json#",
  "build_dependencies": [],
  "build_subdirectory": ".",
  "category": "Utilities",
  "scm_revision": "main",
  "scm_url": "REPO_URL_HERE",
  "tier": 1
}
EOF

# Validate JSON
python3 -c "import json; json.load(open('${EXT_NAME}.json'))" && echo "[OK] JSON is valid" || echo "FAIL: Invalid JSON"
```

**For SlicerMouseMaster:**

```json
{
  "$schema": "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json#",
  "build_dependencies": [],
  "build_subdirectory": ".",
  "category": "Utilities",
  "scm_revision": "main",
  "scm_url": "https://github.com/benzwick/SlicerMouseMaster.git",
  "tier": 1
}
```

### Phase 5: Configure GitHub Repository

```bash
echo "=== Phase 5: GitHub Repository Configuration ==="

# Add 3d-slicer-extension topic (requires gh CLI)
if command -v gh &> /dev/null; then
  echo "Adding '3d-slicer-extension' topic..."
  gh repo edit --add-topic 3d-slicer-extension
else
  echo "Manual step required:"
  echo "1. Go to your repository on GitHub"
  echo "2. Click the gear icon next to 'About'"
  echo "3. Add '3d-slicer-extension' to Topics"
  echo "4. Click Save"
fi

# Disable unused features
echo ""
echo "Manual step required - disable unused GitHub features:"
echo "1. Go to Settings > General"
echo "2. Uncheck: Wiki, Projects, Discussions (if not used)"
echo "3. In About section, uncheck: Releases, Packages (if not used)"
```

### Phase 6: Commit and Push Changes

```bash
echo "=== Phase 6: Commit and Push ==="

# Stage changes
git add CMakeLists.txt
git add LICENSE.txt LICENSE LICENSE.md 2>/dev/null || true
git add README.md

# Commit
git commit -m "chore: prepare for Extension Index submission

- Update CMakeLists.txt metadata
- Ensure LICENSE and README present
"

# Push
git push origin main
```

### Phase 7: Fork and Submit to ExtensionsIndex

```bash
echo "=== Phase 7: Submit to ExtensionsIndex ==="

# Fork ExtensionsIndex (if not already)
if command -v gh &> /dev/null; then
  gh repo fork Slicer/ExtensionsIndex --clone=false
  echo "[OK] Forked ExtensionsIndex"

  # Clone the fork
  gh repo clone YOUR_USERNAME/ExtensionsIndex /tmp/ExtensionsIndex
  cd /tmp/ExtensionsIndex

  # Copy JSON file
  cp /path/to/ExtensionName.json .

  # Commit and push
  git add ExtensionName.json
  git commit -m "Add ExtensionName extension"
  git push origin main

  # Create PR
  gh pr create \
    --repo Slicer/ExtensionsIndex \
    --title "Add ExtensionName extension" \
    --body "$(cat << 'PREOF'
# New extension

## Tier 1

- [x] Extension has a reasonable name
- [x] Repository name is Slicer+ExtensionName
- [x] Repository has 3d-slicer-extension topic
- [x] Extension description summarizes functionality
- [x] No known related patents
- [x] LICENSE.txt present with permissive license
- [x] Extension URL and revision correct
- [x] Icon URL correct
- [x] Screenshot URLs correct
- [x] JSON consistent with CMakeLists.txt
- [x] Homepage contains required information
- [x] Unused GitHub features hidden
- [x] Extension is safe

PREOF
)"
else
  echo "Manual submission required:"
  echo "1. Fork https://github.com/Slicer/ExtensionsIndex"
  echo "2. Add your JSON file to the fork"
  echo "3. Create pull request"
  echo "4. Fill out the PR template checklist"
fi
```

### Phase 8: Post-Submission

```bash
echo "=== Phase 8: Post-Submission ==="

echo "After PR is submitted:"
echo "1. Wait for automated build tests"
echo "2. Respond to reviewer feedback"
echo "3. Extension will appear in Extensions Manager after merge"
echo ""
echo "Monitor PR status at:"
echo "https://github.com/Slicer/ExtensionsIndex/pulls"
```

---

## Complete Submission Script

Copy and customize this script for automated submission:

```bash
#!/bin/bash
# Slicer Extension Index Submission Script
# Customize variables below before running

set -e

# Configuration
EXTENSION_NAME="SlicerMouseMaster"
GITHUB_OWNER="benzwick"
REPO_NAME="SlicerMouseMaster"
CATEGORY="Utilities"
BRANCH="main"

# Paths
EXTENSION_ROOT="/path/to/extension"
JSON_OUTPUT="${EXTENSION_NAME}.json"

echo "Slicer Extension Index Submission"
echo "================================="

# Phase 1: Fetch requirements
echo "Fetching latest requirements..."
curl -sf "https://raw.githubusercontent.com/Slicer/ExtensionsIndex/main/.github/PULL_REQUEST_TEMPLATE.md" > /dev/null || { echo "Failed to fetch PR template"; exit 1; }
curl -sf "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json" > /dev/null || { echo "Failed to fetch schema"; exit 1; }
echo "[OK] Requirements fetched"

# Phase 2-3: Validate (run /validate-extension-submission)
cd "$EXTENSION_ROOT"
echo "Validating extension..."
# Add validation commands here

# Phase 4: Generate JSON
echo "Generating JSON..."
cat > "$JSON_OUTPUT" << EOF
{
  "\$schema": "https://raw.githubusercontent.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json#",
  "build_dependencies": [],
  "build_subdirectory": ".",
  "category": "$CATEGORY",
  "scm_revision": "$BRANCH",
  "scm_url": "https://github.com/$GITHUB_OWNER/$REPO_NAME.git",
  "tier": 1
}
EOF
echo "[OK] JSON generated: $JSON_OUTPUT"

# Validate JSON
python3 -c "import json; json.load(open('$JSON_OUTPUT'))" || { echo "Invalid JSON"; exit 1; }

echo ""
echo "Next steps:"
echo "1. Review generated JSON: cat $JSON_OUTPUT"
echo "2. Fork Slicer/ExtensionsIndex on GitHub"
echo "3. Add $JSON_OUTPUT to your fork"
echo "4. Create PR with completed checklist"
```

---

## Troubleshooting

### PR Build Fails

1. Check build logs on CDash
2. Common issues:
   - Missing dependencies in build_dependencies
   - Wrong build_subdirectory for superbuild
   - CMakeLists.txt syntax errors

### Extension Not Appearing

1. Verify PR was merged
2. Check you're using Slicer Preview Release
3. Clear Extensions Manager cache

### Reviewer Requests Changes

1. Update extension repository
2. If using branch name in scm_revision, changes auto-update
3. If using commit hash, update JSON and push to fork

---

## Related Skills

- `/extension-submission-checklist` - Full checklist reference
- `/prepare-extension-metadata` - Generate metadata files
- `/validate-extension-submission` - Validate before submission
