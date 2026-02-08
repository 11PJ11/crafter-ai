# Agent Definition Best Practices (Evidence-Based)

Research-validated guidelines for creating Claude Code agents. Source: 18 verified sources including Anthropic official docs, academic research, and industry frameworks. Full citations in `docs/research/agent-design/agent-definition-best-practices-comprehensive-research.md`.

## 1. Use the Official Claude Code Format

Anthropic's required structure (from code.claude.com/docs/en/sub-agents):

```markdown
---
name: agent-name
description: When Claude should use this agent. Claude reads this to decide delegation.
tools: Read, Glob, Grep, Bash
model: inherit
maxTurns: 30
skills:
  - relevant-skill-name
---

You are [Name], a [role]. [Goal in one sentence.]

[System prompt as markdown - this is ALL the agent receives as instructions.]
```

**Only `name` and `description` are required** in frontmatter. Other supported fields: `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`.

The markdown body IS the system prompt. Agents receive only this prompt plus basic environment details -- NOT the full Claude Code system prompt, NOT CLAUDE.md.

## 2. Optimal Size: 200-400 Lines

Evidence from three converging sources:

- **A/B test data**: Light (626 lines, 30KB) won 3/4 tasks at ~40-48k tokens. Original (2688 lines, 128KB) cost ~120k tokens with no quality advantage. Ultra-light (211 lines, 12KB) failed 1/4 tasks.
- **Context rot research** (Chroma, 18 models): Accuracy degrades progressively with input length. Focused prompts (~300 tokens) substantially outperform full context (~113k tokens).
- **Underspecification research** (arxiv:2505.13360): 65.2% of explicit prompt requirements duplicate default LLM behaviors. Bayesian optimization cut prompt length 41-45% while improving accuracy 3.8%.

**Target**: 200-400 lines for the agent definition. Domain knowledge goes in Skills.

## 3. Selective Specification (Specify Only Divergences)

Do NOT specify behaviors Claude already does by default. Specify ONLY:
- Behaviors that diverge from Claude's natural tendencies
- Domain-specific rules the model cannot know
- Critical constraints where violation causes real harm

**Remove from agent definitions**:
- File operation instructions (Claude knows how to use Read/Write/Edit)
- Bash usage guidelines (Claude knows tool conventions)
- Generic quality principles ("be thorough", "be accurate")
- Safety frameworks that duplicate Claude Code platform features

**Keep in agent definitions**:
- Domain methodology (TDD phases, architectural patterns)
- Project-specific conventions (naming, file locations, commit formats)
- Non-obvious constraints (test budget formula, hexagonal boundary rules)
- 3-5 canonical examples for critical/subtle behaviors

## 4. Agent Definition Template

```markdown
---
name: {id}
description: Use for {domain}. {When to delegate - one sentence.}
model: inherit
tools: [{only tools this agent needs}]
maxTurns: 30
skills:
  - {domain-knowledge-skill}
---

# Role and Goal

You are {Name}, a {role} specializing in {domain}.
Your goal is {measurable success criteria}.

# Core Method

{3-7 principles that DIVERGE from Claude's defaults.}

1. {Principle}: {brief rationale}
2. {Principle}: {brief rationale}
3. {Principle}: {brief rationale}

# Workflow

1. {Step}
2. {Step}
3. {Step}

# Critical Rules

{3-5 rules where violation causes real harm.}

- {Rule}: {one-line rationale}
- {Rule}: {one-line rationale}

# Examples

{2-4 canonical examples for the most important/subtle decisions.}

## Example: {Scenario}
{Input} -> {Expected behavior}

# Constraints

- {Scope boundary}
- {What this agent does NOT do}
```

## 5. Extract Domain Knowledge into Skills

Anthropic's Skills architecture uses progressive disclosure:
1. **Level 1**: Skill name/description pre-loaded (~50 tokens per skill)
2. **Level 2**: Full SKILL.md loaded when Claude determines relevance
3. **Level 3+**: Referenced files loaded as needed

**Migration pattern**: Move embedded knowledge from agent `.md` into skill directories. Agent references skills in frontmatter. Claude loads only what the current task requires.

Example: software-crafter's TDD methodology, refactoring catalog, and test patterns each become separate skills loaded on demand instead of consuming 2000+ lines in the agent definition.

## 6. Language and Tone for Opus 4.6

Anthropic explicitly warns (platform.claude.com/docs):
- "Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'"
- "Remove over-prompting. Tools that undertriggered in previous models are likely to trigger appropriately now."
- Opus 4.6 "may overtrigger" on aggressive language from older prompt patterns.

**Replace**: "CRITICAL:", "MANDATORY:", "ABSOLUTE NO", "BLOCKER - no exceptions"
**With**: Direct, calm statements. "Do X" not "You MUST ALWAYS do X."

## 7. Safety: Leverage the Platform

Claude Code provides these safety features natively -- do NOT reimplement in agent definitions:
- **Tool restrictions**: `tools` and `disallowedTools` in frontmatter
- **Permission modes**: `permissionMode` field (default/acceptEdits/dontAsk/plan/bypassPermissions)
- **Lifecycle hooks**: PreToolUse, PostToolUse, SubagentStart, SubagentStop
- **Subagent isolation**: Own context window, cannot spawn sub-subagents
- **Turn limits**: `maxTurns` field
- **Audit trails**: Transcript persistence in `~/.claude/projects/`

Agent definitions should declare safety via frontmatter fields and hooks, not prose paragraphs describing security layers.

## 8. Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Monolithic agent (2000+ lines) | Context rot degrades accuracy; 3x token cost | Extract to Skills, target 200-400 lines |
| Embedded safety frameworks | Duplicates Claude Code platform; wastes tokens | Use frontmatter fields and hooks |
| Aggressive language (CRITICAL, MANDATORY) | Causes overtriggering on Opus 4.6 | Use calm, direct statements |
| Zero examples (ultra-light) | Agent fails on subtle/critical behaviors | Include 3-5 canonical examples |
| Exhaustive examples (30+) | Diminishing returns; context rot | Keep 3-5 diverse, canonical cases |
| Specifying default behaviors | 65% of specifications are redundant | Specify only divergent behaviors |
| Negatively phrased rules | "Do not X" less effective than "Do Y instead" | Phrase affirmatively |
| Compound multi-step instructions | Confuses agent reasoning | Split into separate, focused steps |
| Inconsistent terminology | Amplifies confusion in longer contexts | One term per concept throughout |

## 9. Validation Checklist for New Agents

Before finalizing any agent definition:

- [ ] Uses official YAML frontmatter format (name, description required)
- [ ] Total definition under 400 lines (domain knowledge in Skills)
- [ ] Only specifies behaviors that diverge from Claude defaults
- [ ] No aggressive signaling language (CRITICAL, MANDATORY, ABSOLUTE)
- [ ] 3-5 canonical examples for critical behaviors
- [ ] Tools restricted to minimum needed (least privilege)
- [ ] maxTurns set in frontmatter
- [ ] Safety via platform features (frontmatter/hooks), not prose
- [ ] Instructions phrased affirmatively ("Do X" not "Don't do Y")
- [ ] Consistent terminology throughout
- [ ] Description field clearly states when Claude should delegate to this agent
