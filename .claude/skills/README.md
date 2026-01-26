# SlicerMouseMaster Claude Skills

This directory contains Claude Code skills for automating common tasks in the SlicerMouseMaster extension development and deployment workflow.

## What Are Skills?

Skills are structured instructions that guide Claude through specific tasks. Each skill defines:
- When to use it
- Step-by-step procedures
- Code snippets and commands
- Validation checks
- Troubleshooting guidance

Invoke skills by typing `/skill-name` in Claude Code.

---

## Skills Overview

| Skill | Category | Purpose |
|-------|----------|---------|
| `/add-mouse-profile` | Development | Create support for a new mouse model |
| `/detect-buttons` | Development | Discover Qt button codes for unknown mice |
| `/export-preset` | User | Export and share preset configurations |
| `/test-bindings` | Development | Debug and verify button bindings |
| `/extension-submission-checklist` | Submission | Review official Slicer requirements |
| `/prepare-extension-metadata` | Submission | Generate CMakeLists.txt and JSON metadata |
| `/validate-extension-submission` | Submission | Automated validation before submission |
| `/submit-to-extension-index` | Submission | Complete submission workflow |

---

## Recommended Workflow Order

### For Adding Mouse Support

```
1. /detect-buttons        # Discover button codes
2. /add-mouse-profile     # Create profile JSON
3. /test-bindings         # Verify bindings work
4. /export-preset         # Share default preset
```

### For Extension Index Submission

```
1. /extension-submission-checklist    # Review all requirements
2. /prepare-extension-metadata        # Update CMakeLists.txt, generate JSON
3. /validate-extension-submission     # Run automated checks
4. /submit-to-extension-index         # Complete submission process
```

---

## Skill Details

### Development Skills

#### `/add-mouse-profile`

**Purpose**: Create a new mouse profile for a mouse model not yet supported.

**When to Use**:
- Adding support for a new mouse (e.g., Razer, Corsair, SteelSeries)
- User provides vendor/product IDs
- After running `/detect-buttons` to get Qt codes

**Output**:
- `MouseMaster/Resources/MouseDefinitions/<profile_id>.json`
- `presets/builtin/default_<profile_id>.json`
- Updated `README.md` supported mice table

**Limitations**:
- Requires accurate Qt button codes (use `/detect-buttons` first)
- Cannot auto-detect vendor/product IDs
- User must provide mouse specifications

---

#### `/detect-buttons`

**Purpose**: Interactively discover Qt button codes for an unknown mouse.

**When to Use**:
- User has a mouse not in built-in profiles
- Verifying button codes on a specific platform
- Debugging button detection issues

**Output**:
- List of detected button codes
- Mapping guidance (code → physical button)

**Limitations**:
- Requires running code in Slicer's Python console
- Cannot detect buttons intercepted by system/drivers
- Platform-specific behavior (codes may differ on Windows/macOS/Linux)
- Vendor software (Logitech Options, Razer Synapse) may remap buttons

**Caveats**:
- User must have Slicer running
- Some mice require disabling vendor software for accurate detection
- Linux users may need to be in the `input` group

---

#### `/test-bindings`

**Purpose**: Debug and verify button bindings are working correctly.

**When to Use**:
- Binding isn't triggering expected action
- Verifying configuration after changes
- Debugging context-sensitive bindings

**Output**:
- Diagnostic information about module status
- Current binding configuration
- Real-time button press monitoring

**Limitations**:
- Requires Slicer running with MouseMaster module loaded
- Cannot test bindings outside of Slicer
- Some diagnostics require internal API access

---

#### `/export-preset`

**Purpose**: Export a preset configuration for sharing or backup.

**When to Use**:
- Sharing a preset with the community
- Backing up preset configurations
- Contributing presets to the project

**Output**:
- Exported JSON file
- Sharing instructions for GitHub Discussions

**Limitations**:
- Requires preset to exist in user directory
- Cannot validate that preset works on other mice
- No automatic upload to community repository

---

### Extension Submission Skills

#### `/extension-submission-checklist`

**Purpose**: Complete reference of official Slicer Extension Index requirements.

**When to Use**:
- Planning extension submission
- Reviewing what's needed before starting
- Ensuring all requirements are met

**Output**:
- Tier 1/3/5 requirement checklists
- Submission process steps
- Example JSON and metadata

**Critical Feature**:
Always fetches latest requirements from:
- `github.com/Slicer/ExtensionsIndex/.github/PULL_REQUEST_TEMPLATE.md`
- `github.com/Slicer/Slicer/main/Schemas/slicer-extension-catalog-entry-schema-v1.0.1.json`

**Limitations**:
- Checklist is reference only; doesn't perform automated checks
- Some requirements need manual verification (e.g., "follows UI conventions")
- Tier 3/5 requirements may require ongoing commitment

---

#### `/prepare-extension-metadata`

**Purpose**: Generate and update required metadata files for submission.

**When to Use**:
- Ready to prepare files for submission
- CMakeLists.txt has placeholder values
- Need to create Extension Index JSON file

**Output**:
- Updated `CMakeLists.txt` with correct metadata
- `ExtensionName.json` for ExtensionsIndex repository

**Critical Feature**:
Always fetches latest JSON schema to verify required fields.

**Limitations**:
- Requires user to provide accurate URLs and contributor info
- Cannot auto-generate screenshots
- Cannot verify URLs are accessible until after committing

**Caveats**:
- Icon must be 128x128 PNG (recommended)
- Screenshot URLs must be raw GitHub URLs (`raw.githubusercontent.com`)
- Description should be 1-2 sentences, no line breaks

---

#### `/validate-extension-submission`

**Purpose**: Automated validation of all submission requirements.

**When to Use**:
- Before creating submission PR
- After making changes to verify nothing broke
- Quick health check of extension

**Output**:
- Pass/fail status for each requirement
- Specific failure messages with remediation
- Summary of readiness

**Critical Feature**:
Always fetches latest requirements before validating. Alerts if schema version changes.

**Limitations**:
- Cannot verify:
  - Extension builds in Slicer (requires Slicer build environment)
  - Cross-platform compatibility
  - UI/UX conventions compliance
  - Documentation quality
- `gh` CLI required for some GitHub checks
- Network access required to test URL accessibility

**Caveats**:
- Some checks require repository to be pushed to GitHub first
- "3d-slicer-extension" topic check requires `gh` CLI authentication

---

#### `/submit-to-extension-index`

**Purpose**: Complete guided workflow for Extension Index submission.

**When to Use**:
- Ready to submit extension
- Want step-by-step guidance through entire process
- Need to create the PR to ExtensionsIndex

**Output**:
- Updated metadata files
- Generated JSON file
- Pull request to ExtensionsIndex (if `gh` CLI available)

**Critical Feature**:
Fetches and verifies latest requirements at the start of the workflow.

**Limitations**:
- Cannot:
  - Build and test extension in Slicer
  - Respond to reviewer feedback automatically
  - Guarantee PR acceptance
- `gh` CLI required for automated PR creation
- Manual steps required for some GitHub settings

**Caveats**:
- Extension must be pushed to public GitHub repository first
- PR review may take days/weeks depending on reviewer availability
- Tier assignment is determined by reviewers based on checklist completion

---

## Known Issues and Limitations

### General Limitations

1. **Slicer Environment Required**: Most skills require Slicer to be running
2. **No Build Verification**: Skills cannot verify extension builds successfully
3. **Platform-Specific Behavior**: Button codes and behaviors differ across OS
4. **Manual Steps**: Some tasks cannot be fully automated

### Network Dependencies

- Submission skills require internet access to fetch latest requirements
- URL validation requires network access
- GitHub operations require `gh` CLI authentication

### Missing Automation

Things that currently require manual action:
- Building and testing extension in Slicer
- Creating screenshots
- Writing documentation
- Responding to PR reviews
- Cross-platform testing

---

## Things That Might Not Work

### Platform-Specific Issues

| Issue | Platform | Workaround |
|-------|----------|------------|
| Button not detected | macOS | System may intercept; check System Preferences |
| Button not detected | Linux | Add user to `input` group |
| Wrong button code | All | Disable vendor software (Logitech Options, etc.) |
| URL check fails | All | Check firewall/proxy settings |

### GitHub CLI Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "gh: command not found" | CLI not installed | Install via `brew install gh` or equivalent |
| "authentication required" | Not logged in | Run `gh auth login` |
| "repository not found" | Wrong URL | Verify repository exists and is public |

### Slicer Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Module not found | Not installed | Install via Extension Manager |
| Logic not initialized | Module not opened | Open MouseMaster module first |
| Event handler not active | Disabled | Click Enable button in module |

---

## Future Skills (Not Yet Implemented)

### High Priority

| Skill | Purpose | Complexity |
|-------|---------|------------|
| `/create-screenshot` | Generate module screenshots for submission | Medium |
| `/verify-slicer-build` | Test extension builds in Slicer | High |
| `/run-integration-tests` | Run tests inside Slicer | Medium |
| `/update-version` | Bump version numbers consistently | Low |

### Medium Priority

| Skill | Purpose | Complexity |
|-------|---------|------------|
| `/generate-release-notes` | Create release notes from commits | Medium |
| `/sync-preset-repository` | Sync presets with community repo | Medium |
| `/migrate-preset-format` | Upgrade preset to new schema version | Low |
| `/analyze-button-usage` | Suggest bindings based on user patterns | High |

### Low Priority

| Skill | Purpose | Complexity |
|-------|---------|------------|
| `/import-logitech-options` | Import settings from Logitech software | High |
| `/generate-documentation` | Auto-generate docs from code | Medium |
| `/localize-preset` | Translate preset names/descriptions | Low |

---

## Contributing New Skills

### Skill File Structure

```
.claude/skills/
└── skill-name/
    └── SKILL.md
```

### Required Sections

Every skill SKILL.md should include:

1. **Title and Description**: What the skill does
2. **When to Use**: Clear triggers for when to invoke
3. **Steps**: Numbered procedure with code examples
4. **Output**: What the skill produces
5. **Limitations**: What it cannot do
6. **Troubleshooting**: Common issues and solutions

### Best Practices

- **Fetch live requirements**: Submission skills should always verify against latest official sources
- **Provide validation**: Include checks to verify success
- **Handle errors**: Document common failure modes
- **Be platform-aware**: Note platform-specific differences
- **Include examples**: Show expected input/output

### Example Template

```markdown
# Skill Name

Brief description of what this skill does.

## When to Use

Use this skill when:
- Trigger condition 1
- Trigger condition 2

## Steps

1. **Step Name**
   Description and code...

2. **Step Name**
   Description and code...

## Output

- Output file 1
- Output file 2

## Limitations

- Cannot do X
- Requires Y

## Troubleshooting

### Issue Name
Solution...
```

---

## Maintenance

### Updating Skills

When Slicer requirements change:

1. Fetch latest PR template and schema
2. Compare against skill content
3. Update affected skills
4. Note schema version in skill header
5. Test skills with current Slicer version

### Version Tracking

Current verified versions:
- **PR Template**: Fetched live (always current)
- **JSON Schema**: v1.0.1 (2025-01-26)
- **Slicer**: 5.4+

---

## Support

- **Issues**: Report skill bugs at https://github.com/benzwick/SlicerMouseMaster/issues
- **Slicer Forum**: https://discourse.slicer.org for extension questions
- **Extension Docs**: https://slicer.readthedocs.io/en/latest/developer_guide/extensions.html
