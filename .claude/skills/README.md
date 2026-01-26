# SlicerMouseMaster Claude Skills & Agents

This directory contains Claude Code skills and agents for automating common tasks in the SlicerMouseMaster extension development and deployment workflow.

## What Are Skills?

Skills are structured instructions that guide Claude through specific tasks. Each skill defines:
- When to use it
- Step-by-step procedures
- Code snippets and commands
- Validation checks
- Troubleshooting guidance

Invoke skills by typing `/skill-name` in Claude Code.

---

## Agents

Agents are autonomous workflows that combine multiple skills. Located in `.claude/agents/`.

| Agent | Purpose |
|-------|---------|
| `test-runner` | Run tests + lint + audit + report in one workflow |

### Using Agents

Ask Claude to run an agent:
```
Run the test-runner agent
```

Agents can:
- Run multiple checks autonomously
- Fix simple issues automatically
- Generate reports
- Escalate complex issues to humans

---

## Platform Verification

Track cross-platform testing status in `docs/platform-matrix.md`.

| Platform | Status |
|----------|--------|
| Linux | ✓ Primary dev |
| Windows | ⏳ Pending |
| macOS | ⏳ Pending |

Update the matrix when verifying on new platforms.

---

## Code Quality Philosophy

This project follows **fail-fast, test-driven development** designed for human-LLM collaboration:

### Principles

1. **Fail Fast** - Errors surface immediately, never hidden
2. **Explicit Over Silent** - No `except: pass`, no silent `continue`
3. **Log Everything** - All exceptions logged for debugging
4. **Test First** - Tests catch bugs, not error suppression
5. **Clear Signals** - Detailed logs enable autonomous debugging

### Why This Matters for LLM Collaboration

When Claude Code works on this codebase:

- **Clear test output** - Claude can run tests and understand results
- **Explicit errors** - Claude can identify and fix real issues
- **Detailed logs** - Claude can trace problems through execution
- **No hidden state** - Code behavior matches what Claude reads
- **Autonomous maintenance** - Claude can audit, fix, and verify without hand-holding

### Anti-Patterns (Never Use)

```python
# NEVER: Silent exception swallowing
except: pass
except Exception: pass

# NEVER: Silent continuation
if error: continue

# NEVER: Hidden None returns
if bad: return None

# NEVER: Unlogged exceptions
except SomeError:
    return default  # No logging!
```

### Correct Patterns

```python
# CORRECT: Specific exception + logging + action
except SpecificError as e:
    logger.exception("Failed to X: %s", e)
    raise  # or handle specifically

# CORRECT: Explicit error collection
if not valid:
    errors.append(f"Invalid: {item}")
if errors:
    raise ValueError(f"Validation failed: {errors}")

# CORRECT: Documented intentional handling
try:
    optional_feature()
except ImportError:
    logger.info("Optional feature unavailable")  # Intentional, documented
```

---

## Skills Overview

| Skill | Category | Purpose |
|-------|----------|---------|
| `/add-mouse-profile` | Development | Create support for a new mouse model |
| `/detect-buttons` | Development | Discover Qt button codes for unknown mice |
| `/export-preset` | User | Export and share preset configurations |
| `/test-bindings` | Development | Debug and verify button bindings |
| `/run-tests` | Code Quality | Run tests + lint + typecheck + audit |
| `/audit-code-quality` | Code Quality | Scan for bad practices (fail-fast violations) |
| `/fix-bad-practices` | Code Quality | Fix exception swallowing and error hiding |
| `/autonomous-code-review` | Code Quality | Full autonomous code review and fix workflow |
| `/generate-screenshots` | Submission | Capture UI screenshots for documentation |
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
1. /generate-screenshots              # Capture UI screenshots (requires Slicer)
2. /extension-submission-checklist    # Review all requirements
3. /prepare-extension-metadata        # Update CMakeLists.txt, generate JSON
4. /validate-extension-submission     # Run automated checks
5. /submit-to-extension-index         # Complete submission process
```

### For Code Quality Maintenance

```
/run-tests                    # Quick: tests + lint + typecheck + audit
```

Or for detailed work:

```
1. /audit-code-quality        # Detailed scan for bad practices
2. /fix-bad-practices         # Fix identified issues
3. /run-tests                 # Verify fixes
```

Or fully autonomous:

```
/autonomous-code-review       # Full audit, fix, and verify cycle
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

### Code Quality Skills

These skills enforce **fail-fast, test-driven development** principles. The codebase philosophy:

- **Errors should surface immediately** - Never hide or swallow errors
- **Exceptions are for exceptional cases** - Not for flow control
- **All exceptions must be logged** - For human and LLM debugging
- **Tests catch bugs early** - Not error suppression in production
- **Humans and LLMs collaborate** - Clear logs enable autonomous fixing

#### `/audit-code-quality`

**Purpose**: Systematically scan codebase for bad coding practices.

**When to Use**:
- Before committing changes
- During code review
- Periodically for maintenance
- Autonomously as part of CI

**Detects**:
- `except: pass` and `except Exception: pass` (CRITICAL)
- Overly broad exception handling (HIGH)
- Silent `if error: continue` patterns (MEDIUM)
- Missing exception logging (MEDIUM)
- `return None` hiding errors (LOW)
- Ignored subprocess return values (MEDIUM)

**Output**:
- Categorized list of issues by severity
- File locations and line numbers
- Code context for each issue

**Limitations**:
- Pattern-based detection may have false positives
- Cannot determine developer intent
- Some patterns require manual review
- Does not auto-fix issues

---

#### `/fix-bad-practices`

**Purpose**: Fix bad coding practices following fail-fast principles.

**When to Use**:
- After running `/audit-code-quality`
- When fixing specific anti-patterns
- During code quality refactoring

**Fix Patterns**:

| Bad Pattern | Fix |
|-------------|-----|
| `except: pass` | Specific exception + logging + re-raise |
| `except Exception` | Specific exception types |
| Silent `continue` | Explicit error handling or logging |
| `return None` on error | Raise exception with context |
| Error return codes | Raise exceptions instead |
| subprocess without check | Add `check=True` |

**Output**:
- Transformed code following best practices
- Added logging where missing
- Proper exception handling

**Limitations**:
- Requires understanding context before applying fix
- Some fixes may need manual adjustment
- Must run tests after each fix
- Cannot fix complex conditional logic automatically

**Caveats**:
- Always run tests after fixing
- Review fixes before committing
- Some "bad" patterns may be intentional (document why)

---

#### `/autonomous-code-review`

**Purpose**: Run complete code quality workflow without human intervention.

**When to Use**:
- For regular maintenance
- When instructed to "review and fix code"
- After completing a feature
- As scheduled quality check

**Workflow**:
1. **Assess** - Run tests, linting, type checking
2. **Audit** - Scan for all bad practices
3. **Prioritize** - Sort issues by severity
4. **Fix** - Apply fixes one at a time
5. **Verify** - Run tests after each fix
6. **Report** - Generate summary of changes

**Output**:
- Fixed code with proper error handling
- Test verification for each fix
- Summary report of all changes
- List of issues requiring human review

**Autonomous Capabilities**:
- Run tests without prompting
- Identify and categorize issues
- Apply standard fix patterns
- Verify fixes don't break tests
- Generate clear reports

**Limitations**:
- Cannot fix issues that cause test failures without investigation
- Cannot determine business logic intent
- May flag intentional patterns as issues
- Cannot access Slicer runtime for integration tests

**When Human Review Needed**:
- Complex exception handling with multiple branches
- Critical paths (data persistence, security)
- Patterns marked with explanatory comments
- Any fix that causes test failures

**Decision Rules**:
- Auto-fix: Simple patterns (`except:pass`, missing `check=True`)
- Flag for review: Complex logic, critical paths
- Skip: Test files, vendored code, commented explanations

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

### Code Quality Skill Limitations

The code quality skills have specific limitations:

| Limitation | Reason | Workaround |
|------------|--------|------------|
| False positives | Pattern-based detection | Manual review flagged items |
| Cannot determine intent | No semantic understanding | Add comments explaining patterns |
| Test files flagged | May test error conditions | Exclude test directories |
| Complex logic | Cannot reason about flow | Human review required |
| Runtime behavior | Static analysis only | Slicer integration tests needed |

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
