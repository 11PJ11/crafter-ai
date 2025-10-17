# Claude Code Model Selection - Implementation Guide

**Purpose**: Step-by-step instructions to implement the user's goal of using Haiku for reviews and Sonnet for implementation

**Status**: Fully supported, ready to implement

---

## Prerequisites Check

1. Claude Code version: Ensure v1.0.57 or later
   - Verify: `@claude /status` and check version
   - If older: Update to latest version

2. Available models: Confirm access to Haiku and Sonnet
   - Verify: `@claude /model` to see available options
   - Should show: `haiku`, `sonnet`, `opus`

---

## Step 1: Create Review Command (Haiku-Optimized)

**File**: `.claude/commands/review.md`

```yaml
---
name: review
model: haiku
allowed-tools: Read
argument-hint: [file-path]
description: Fast code review using Haiku for efficiency
---

You are a fast code reviewer optimized for identifying issues quickly.

Review the file at $ARGUMENTS and identify:

1. **Bugs**: Logic errors, null checks, boundary conditions
2. **Security Issues**: Input validation, injection vulnerabilities
3. **Performance**: Obvious inefficiencies, unnecessary loops
4. **Style**: Naming conventions, formatting issues

Format your response as concise bullet points. Be direct.

Example format:
- Line 42: Missing null check on user object
- Function name should be `calculateTotal` not `calc`
- Use `const` instead of `let` for immutable bindings
```

**Why Haiku?**
- Reviews are typically simple pattern-matching tasks
- Haiku 4.5 has "near-frontier performance" for this
- Significant cost savings on high-volume reviews
- 30-50% faster than Sonnet

---

## Step 2: Create Implementation Command (Sonnet-Optimized)

**File**: `.claude/commands/implement.md`

```yaml
---
name: implement
model: sonnet
allowed-tools: Read, Write, Bash
argument-hint: [feature-description]
description: Complex implementation using Sonnet for full capability
---

You are a senior engineer implementing complex features.

Implement the following feature: $ARGUMENTS

Provide:

1. **Architecture**: How components fit together, data flow
2. **Implementation**: Complete code with all edge cases
3. **Testing**: Unit test examples for edge cases
4. **Documentation**: Docstrings and comments where needed
5. **Considerations**: Performance, security, maintainability notes

Think deeply about design before implementing. Ensure production-quality code.
```

**Why Sonnet?**
- Implementation requires deep reasoning and architecture decisions
- Sonnet 4.5 is "best model for complex coding"
- Worth the higher cost for quality and thoughtfulness
- Reduces debugging/rework time

---

## Step 3: Create Flexible Helper Subagent (Optional)

**File**: `.claude/agents/helper.md`

```yaml
---
name: helper
model: inherit
description: Flexible helper that adapts to session model choice
tools: Read, Write, Bash
---

You are a helpful coding assistant. You assist with various tasks
including code analysis, debugging, refactoring, and documentation.

When delegated a task, provide clear, practical solutions.
Adapt your depth and explanation style to match the context.

Your capabilities:
- Code analysis and optimization
- Bug identification and fixing
- Refactoring recommendations
- Documentation generation
- Testing strategies
```

**Why `inherit`?**
- Allows user to control subagent model via `/model` command
- Useful for varying complexity levels
- Adapts automatically to user's session choice

---

## Step 4: Configure Project Defaults (Recommended)

**File**: `.claude/settings.json`

```json
{
  "model": "haiku",
  "testCommand": "npm test",
  "lintCommand": "npm lint",
  "project": "ai-craft",
  "description": "Development configuration - Haiku by default, override with specific commands"
}
```

**Effect**:
- Default `/` commands use Haiku (fast, economical)
- `/review` uses Haiku (explicit specification)
- `/implement` uses Sonnet (explicit specification)
- Other commands inherit from project default (Haiku)

**Personal Override** (if needed): `.claude/settings.local.json`

```json
{
  "model": "sonnet"
}
```

This overrides the project default for your local work only (gitignored).

---

## Step 5: Testing and Verification

### Test 1: Verify Command Model Selection

```bash
# In Claude Code session
@claude /review src/myfile.ts
```

**Verify**: Check that response seems concise and fast (Haiku characteristics)

```bash
@claude /implement "Add user authentication with JWT"
```

**Verify**: Check that response is detailed and thorough (Sonnet characteristics)

---

### Test 2: Verify Subagent Model

If you created the helper subagent:

```bash
@claude /delegate helper "Review this code for security issues"
```

**Verify**: Response uses the inherited model (should be Haiku by default from settings)

---

### Test 3: Session Model Override

Test that you can override:

```bash
@claude /model sonnet
@claude /review src/myfile.ts
```

**Expected**: Review command still uses Haiku (frontmatter takes precedence over session)

---

## Step 6: Optimize Prompts for Each Model

### For Haiku Commands (Efficiency Focus)

Structure for maximum clarity in minimal tokens:

```yaml
---
model: haiku
---

Find and list [specific issues] in $ARGUMENTS.

Output format:
- Issue type: brief description
- Location: line number or reference
- Fix: one-liner suggestion

Be concise. No explanations needed.
```

**Optimization**: Short prompts, clear output format, specific requirements

---

### For Sonnet Commands (Capability Focus)

Structure for thoughtful, thorough responses:

```yaml
---
model: sonnet
---

Consider all aspects of $ARGUMENTS:

1. Current state: Analyze what exists
2. Design: Plan the solution thoroughly
3. Implementation: Write complete code
4. Validation: Ensure edge cases handled
5. Reflection: Document tradeoffs and decisions

Think deeply. Quality over speed.
```

**Optimization**: Complex reasoning, full context, detailed requirements

---

## Step 7: Usage Patterns

### High-Volume Review Workflow

```bash
# Review multiple files quickly with Haiku
@claude /review src/component1.ts
@claude /review src/component2.ts
@claude /review src/component3.ts

# Cost: Minimal, very fast responses
```

### Implementation Workflow

```bash
# Get detailed implementation with Sonnet
@claude /implement "User authentication system with JWT tokens"

# Get comprehensive response with architecture, tests, docs
```

### Mixed Workflow

```bash
# Start with implementation (detailed)
@claude /implement "Feature X"

# Quick review of generated code
@claude /review src/featureX.ts

# Delegate helper for refinement
@claude /delegate helper "Optimize the performance"
```

---

## Step 8: Model Selection Based on Complexity

### Simple Tasks → Use Haiku

- Code review for style/obvious bugs
- Quick debugging
- Refactoring suggestions
- Documentation generation
- Simple testing

### Complex Tasks → Use Sonnet

- Architecture design
- Complex implementation
- Deep debugging of subtle issues
- Security analysis
- Performance optimization
- Design pattern selection

### Flexible Tasks → Use Inherit

- Create subagents that adapt
- Let user choose via `/model`
- Delegation tasks that vary

---

## Troubleshooting

### Problem: Command Still Uses Default Model

**Solution**: Verify YAML frontmatter is correct

```yaml
---
name: review
model: haiku
---
```

Check:
- Spaces/indentation (YAML sensitive)
- Model name exactly matches: `haiku`, `sonnet`, or `opus`
- Frontmatter between `---` markers

### Problem: Changes Not Taking Effect

**Solution**: Restart Claude Code session

```bash
@claude /exit
claude
```

New session will reload command definitions.

### Problem: "Model not found" Error

**Solution**: Verify model is available

```bash
@claude /model
# Should display available models including haiku and sonnet
```

If missing, update Claude Code to v1.0.57 or later.

---

## Performance Expectations

### Haiku Model (Reviews)

- **Speed**: 2-3x faster than Sonnet
- **Cost**: ~1/3 cost of Sonnet
- **Quality**: High for pattern-matching tasks
- **Best for**: Quick feedback loops

### Sonnet Model (Implementation)

- **Speed**: Baseline (1x)
- **Cost**: Baseline (1x)
- **Quality**: Highest across most tasks
- **Best for**: Complex work, full context understanding

### Expected Cost Impact (Estimated)

If 70% of commands are reviews (Haiku) and 30% are implementations (Sonnet):

```
Traditional (all Sonnet):   100 tokens/cost units
Optimized (70% Haiku):      ~60 tokens/cost units (40% reduction)
```

---

## Advanced: Environment Variable Override

For temporary testing or CI/CD integration:

```bash
# Force all models to Sonnet for this session
export ANTHROPIC_MODEL=sonnet
claude

# Or override specific model aliases
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-3-5-haiku-20241022
```

---

## Integration with AI-Craft Project

If implementing within the AI-Craft 5D Wave system:

1. **Review Phase** (Wave 1): Use `/review` command with Haiku
2. **Implementation Phase** (Wave 2): Use `/implement` command with Sonnet
3. **Custom Commands**: Create domain-specific commands with appropriate models
4. **Delegation**: Use subagents with `model: inherit` for flexible routing

---

## Validation Checklist

- [ ] Claude Code version is v1.0.57 or later
- [ ] `.claude/commands/review.md` created with `model: haiku`
- [ ] `.claude/commands/implement.md` created with `model: sonnet`
- [ ] `.claude/settings.json` configured with project defaults
- [ ] `/review` command tested and confirmed using Haiku
- [ ] `/implement` command tested and confirmed using Sonnet
- [ ] Subagent (optional) created with `model: inherit`
- [ ] Team documentation updated with command usage
- [ ] Cost analysis performed (if budget-sensitive)

---

## References

- **Official Docs**: https://docs.claude.com/en/docs/claude-code/slash-commands
- **Subagents**: https://docs.claude.com/en/docs/claude-code/sub-agents
- **Model Config**: https://docs.claude.com/en/docs/claude-code/model-config
- **Research Report**: `/mnt/c/Repositories/Projects/ai-craft/data/research/claude-code-model-selection-research.md`
- **Research Summary**: `/mnt/c/Repositories/Projects/ai-craft/data/research/claude-code-model-selection-summary.md`

---

## Questions?

Refer to the comprehensive research report for detailed findings and evidence-based analysis. All claims in this implementation guide are documented in the full research report with citations to official Anthropic documentation.
