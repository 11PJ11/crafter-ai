# NOVEL EDITOR AGENT - ChatGPT Usage Guide

## 📋 Quick Start

### What is this?
An AI agent specialized in editing genre fiction (fantasy, sci-fi, romantasy) using evidence-based techniques from 21 research findings and 24 authoritative sources. Think of it as a professional developmental editor with expertise in plot holes, pacing, character development, and writing style.

### What can it do?
- ✅ Detect plot holes using Character Consistency Framework
- ✅ Analyze pacing (sentence structure, dialogue, scene length)
- ✅ Replicate writing styles (general + specific authors like Titania Blesh)
- ✅ Validate story structure across 7 major frameworks
- ✅ Check character development (wants vs needs)
- ⚠️ Support brainstorming (LIMITED - basic metrics only)
- ✅ Run developmental editing checklist (6 competencies)

---

## 🚀 How to Load the Agent in ChatGPT

### Option 1: Custom Instructions (ChatGPT Plus - Persistent)

**Best for**: Regular use, always-on editor assistant

1. Open ChatGPT
2. Click your profile (bottom left)
3. Select **Settings** → **Personalization** → **Custom Instructions**
4. In "How would you like ChatGPT to respond?", paste the content from:
   ```
   agents/novel-editor-chatgpt-toon.txt
   ```
5. Click **Save**
6. **Activate**: Start a new chat and type: `activate as Aria`

**Benefits**: Agent always available in all new chats

---

### Option 2: Single Conversation (Free & Plus)

**Best for**: One-time analysis, testing

1. Open new ChatGPT chat
2. Copy entire content from `agents/novel-editor-chatgpt-toon.txt`
3. Paste as first message
4. ChatGPT will respond confirming Aria is active
5. Proceed with your editing requests

**Benefits**: No settings changes, works on free tier

---

### Option 3: Custom GPT (ChatGPT Plus Only - Shareable)

**Best for**: Team use, sharing with writing group

1. Go to **Explore GPTs** → **Create a GPT**
2. In "Instructions", paste content from `agents/novel-editor-chatgpt-toon.txt`
3. Name it: **"Aria - Genre Fiction Editor"**
4. Description: "Evidence-based editor for fantasy/sci-fi/romantasy. 21 findings, 24 sources. Plot holes, pacing, style, structure."
5. Set Conversation Starters:
   - "Analyze this scene for plot holes"
   - "Check the pacing of this chapter"
   - "Help me write like [author name]"
   - "Run developmental editing checklist"
6. **Save** and choose sharing: Only me / Anyone with link / Public

**Benefits**: Shareable, persistent, dedicated workspace

---

## 💡 How to Use - Examples & Expected Outputs

### EXAMPLE 1: Plot Hole Detection

#### Your Input:
```
I need help with a plot hole. My protagonist is an expert lockpicker in chapter 3
(she picks a complex safe in 30 seconds). But in chapter 7, she can't open a
simple door lock and has to break the door down instead.

Genre: Fantasy
Context: Both scenes happen within 2 days story-time.
```

#### Expected Output from Aria:
```
ANALYSIS: Plot Hole Detected

CONF: HIGH | F1-CharConsist(WriteP)

ISSUE: Sudden capability change without narrative justification

Pattern: "sudden_capability_changes" - Character shows skill variance inconsistent
with established competence without story-driven reason.

GENRE CONTEXT (Fantasy):
This inconsistency is tolerated ONLY if:
1. Worldbuild explanation (magical interference with locks?)
2. Documented stress/trauma between chapters 3-7
3. Intentional setup for later reveal

CURRENT ASSESSMENT: Problematic - readers will notice the inconsistency

RECOMMENDATIONS (HIGH Priority):

Option A - Add Justification:
[ ] Insert scene in ch 5-6 showing hand injury from combat
[ ] Add internal monologue in ch 7: "Her fingers still trembled from the burns..."

Option B - Establish Lock Difference:
[ ] Establish in ch 7 that this door has anti-magic ward (if your magic system supports)
[ ] Show protagonist attempting pick, magic interferes, forced to break door

Option C - Adjust Ch 3:
[ ] Lower skill demonstration in ch 3 (takes 5 minutes, not 30 seconds)
[ ] Establish she's good but not infallible

BRAINSTORMING PROMPT (Gap7-Limited):
"What event between ch 3-7 could plausibly reduce protagonist's dexterity or lock-picking
ability temporarily?"

SOURCE: Finding 1 - Character Consistency Framework (The Write Practice)
CROSS-REF: Finding 2 - Plot Hole Resolution Strategies (TCK Publishing)
```

---

### EXAMPLE 2: Pacing Analysis

#### Your Input:
```
This chapter feels slow. Can you analyze the pacing and suggest improvements?

[Chapter 5 - 2500 words]
The sun rose over the mountains, painting the snow-capped peaks in shades of gold
and amber. Lysandra watched from her window, thinking about the events of the previous
night. The argument with Marcus had been unexpected. She had always believed their
friendship was unshakeable, but his words had cut deeper than any blade...
[continues for 2500 words with mostly introspection and description]

Genre: Fantasy
```

#### Expected Output from Aria:
```
PACING ANALYSIS: Chapter 5

CONF: HIGH | F5-6-7 (Pacing Techniques)

OBSERVATIONS:

1. SENTENCE STRUCTURE (F5-WriteP):
   - Avg sentence length: ~23 words (estimated from sample)
   - Sentence variance: LOW (consistently long, complex sentences)
   - Pattern: Predominantly descriptive, introspective

2. DIALOGUE-TO-DESCRIPTION RATIO (F5):
   - Estimated: 5% dialogue / 95% description+introspection
   - Genre baseline fantasy: typically 30-40% dialogue for character scenes

3. SCENE TYPE:
   - Current: Pure introspection + description (no action, minimal dialogue)
   - Effect: DECELERATION techniques dominating

DIAGNOSIS: Chapter employs almost exclusively DECEL techniques without balance

GENRE NOTE (F6-LiteraryDevices):
Fantasy permits slow worldbuilding, BUT this appears to be character reflection
scene, not worldbuilding. Slow pacing here may frustrate readers expecting
progression after ch 4 conflict.

RECOMMENDATIONS (MED-HIGH Priority):

IMMEDIATE FIXES (F5-F6-F7):

1. BREAK UP INTROSPECTION (F5):
   [ ] Insert action beats: Lysandra packing, walking, doing something physical
   [ ] Cut sentence length by 30%: avg 23w → 16w
   Example BEFORE: "She had always believed their friendship was unshakeable,
   but his words had cut deeper than any blade"
   Example AFTER: "Their friendship had been unshakeable. Or so she'd thought.
   His words cut deeper than any blade."

2. ADD DIALOGUE (F7-Mythcreants):
   [ ] Insert conversation: servant, another character, even internal dialogue externalized
   [ ] Use rapid-fire technique for tension:
       "Where is Marcus?"
       "Gone."
       "Gone where?"
       "He didn't say."

3. INTERLEAVE ACTION (F6-Reedsy):
   [ ] Lysandra receives letter mid-chapter (plot advancement)
   [ ] Someone interrupts her introspection (conflict introduction)
   [ ] She makes active decision and acts on it

STRUCTURAL SUGGESTION (F6):
Consider TWO-ACT pacing within chapter:
- First 40%: Introspection (current content, compressed)
- Last 60%: Action/dialogue/decision (accelerate toward chapter end)

SPECIFIC TECHNIQUE - DRAMATIC PAUSING (F7):
If keeping introspective opening, use pauses for impact:
"She stared at the mountains. Gold and amber. Beautiful.
[narrative action beat]
And utterly irrelevant. Marcus was gone."

PRIORITY: Address dialogue ratio first (biggest impact), then sentence variance

SOURCE: F5-WriteP (Pacing-Sentence), F6-Reedsy (Pacing-Structural),
F7-Mythcreants (Dialogue-Pacing)
```

---

### EXAMPLE 3: Style Replication

#### Your Input:
```
I want to write with a style similar to Titania Blesh (Italian fantasy author).
What are her signature techniques I should use?
```

#### Expected Output from Aria:
```
STYLE ANALYSIS: Titania Blesh

SRC: F21-Goodreads/Audible (15+ reader reviews analyzed)
CONF: MED-HIGH (based on reader observations, not direct text analysis)

⚠️ LIMITATION: Analysis based on reader reviews. For precise quantitative metrics
(sentence length, metaphor frequency, etc.), would need actual text samples.

8 SIGNATURE PATTERNS (Replicable):

P1. DUAL POV MASTERY ★★★
TECHNIQUE: Alternate between 1st person (one character) and 3rd person (another character)
EXAMPLE: Protagonist Fiammetta = 1st person POV | Antagonist Ambrosio = 3rd person POV
WHY IT WORKS: "the attentive architecture of two voices never felt incoherent" (reader quote)
HOW TO APPLY:
  - Choose your POV split (protagonist 1st, antagonist 3rd)
  - Make voices DISTINCT (different vocabulary, sentence rhythm, concerns)
  - Maintain consistency within each POV

P2. SILENT WORLDBUILDING ★★★
TECHNIQUE: Convey worldbuilding through vocabulary differences and dialogue, NOT exposition
READER QUOTE: "masterclass di silent worldbuilding"
EXAMPLE: Two crab-cities differentiated through language and culture, not info-dump paragraphs
HOW TO APPLY:
  - Delete long worldbuilding paragraphs
  - Show world through: character actions, regional vocabulary, cultural assumptions in dialogue
  - Let reader piece together the world through clues

P3. IMMERSIVE PROSE ★★
TECHNIQUE: Throw reader directly into story without lengthy setup
DESCRIPTION: "Pulito, asciutto come la chitina" (clean, dry like chitin)
READER OBS: "by trilogy end, readers forgot they were reading" (total immersion)
HOW TO APPLY:
  - Start in medias res (middle of action)
  - No informational prologues
  - Trim first chapter by 30% - start later in the action

P4. FLAWED PROTAGONISTS ★★★
TECHNIQUE: Create psychologically complex protagonists, avoid Mary Sue perfection
EXAMPLE: Niniin portrayed with "sense of inadequacy and fear"
READER QUOTE: "strong female characters without being Mary Sues"
HOW TO APPLY:
  - Give protagonist genuine fears (not just "afraid of spiders")
  - Internal contradictions (wants X but needs Y)
  - Moments of failure, self-doubt, poor decisions

P5. DIMENSIONAL ANTAGONISTS ★★
TECHNIQUE: Give antagonists full character arcs with possibility of redemption
EXAMPLE: Ambrosio (book 1 antagonist) "changes profoundly throughout narrative"
READER OBS: "thoughtful emotional development" | Sandros "evolves to sympathetic character"
HOW TO APPLY:
  - Antagonist gets POV chapters (see P1)
  - Show their motivations, not just actions
  - Allow for alliance, redemption arc, or at minimum understanding

P6. TONAL BALANCE ★★
TECHNIQUE: Alternate high-tension scenes with comedic relief
EXAMPLE: Fiammetta's "constant imprecations invoking saints with unusual names"
READER OBS: "creative insults and witty dialogue" between life-threatening moments
HOW TO APPLY:
  - After intense battle/conflict scene, insert humor in next scene
  - Character verbal tics that are funny (Fiammetta's saint invocations)
  - Witty banter during downtime

P7. TWO-ACT PACING ★
TECHNIQUE: Structure with slower first half (setup/worldbuild), accelerated second half
READER OBS: "first half ship reconstruction, second half impossible to put down"
HOW TO APPLY:
  - Book structure: 40% slow burn (worldbuild, char dev) → 60% acceleration (plot, action)
  - Chapter structure: first pages setup → last pages drive to cliffhanger
  - Don't fear slow opening IF payoff delivers

P8. CINEMATIC VISUAL STORYTELLING ★
TECHNIQUE: Describe scenes as if blocking for camera/animation
READER QUOTE: "scenes seemed made for animated adaptation"
DESCRIPTION: "imagery deserving screen translation"
HOW TO APPLY:
  - Write action as shot list: "She ducked. Blade whistled overhead. Roll left."
  - Visual clarity > poetic abstraction
  - Choreograph fights/action like stunt coordinator

PRIORITY RANKING (by impact):
1. P2-Silent Worldbuild (transforms entire manuscript approach)
2. P1-Dual POV (if starting fresh book)
3. P4-Flawed Protag (critical for reader connection)
4. P5-Dimensional Antag (differentiates from generic fantasy)
5. P3-Immersive Prose (keeps readers engaged)
6. P6-Tonal Balance (prevents grimdark fatigue)
7. P8-Cinematic Visuals (especially for action scenes)
8. P7-Two-Act Pacing (structure-level decision)

RECOMMENDED STARTING POINT:
If revising existing manuscript: Start with P2 (Silent Worldbuild) - audit every
worldbuilding paragraph, convert to dialogue/action/vocabulary.

If starting new project: Commit to P1 (Dual POV) + P4 (Flawed Protag) from outline stage.

ADDITIONAL INFO AVAILABLE:
- Published works: 5 books (Piratesse del Mediterraneo trilogy + standalone)
- Genres: Historical Fantasy, YA Fantasy, Sci-Fi
- Themes: Volcanoes, astronomy (author's declared obsessions)
- Availability: Italian originals on Audible Italia

WITH TEXT SAMPLES, I COULD ANALYZE:
- Sentence structure metrics (avg length, complexity patterns)
- Dialogue vs narration exact ratios
- Metaphor frequency and volcano/astronomy imagery usage
- Regional vocabulary patterns
- Character voice distinctiveness in dual POV sections

SOURCE: Finding 21 - Titania Blesh Comprehensive Analysis (Goodreads, Audible Italia,
author website)
```

---

### EXAMPLE 4: Developmental Editing Checklist

#### Your Input:
```
Can you run the developmental editing checklist on my manuscript?

Manuscript: YA Fantasy, 85k words, first draft complete
Title: "The Shattered Crown"
Premise: Princess discovers she's adopted, real heritage is from enemy kingdom's
ruling family. Must prevent war while uncovering conspiracy that led to her kidnapping.
```

#### Expected Output from Aria:
```
DEVELOPMENTAL EDITING CHECKLIST
Manuscript: "The Shattered Crown" (YA Fantasy, 85k)

Based on: Brooks 6 Competencies (F10), Weiland (F11-12), Penn (F13)

NOTE: Without full manuscript access, this is FRAMEWORK-based assessment.
Provide specific scenes/chapters for detailed analysis.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CONCEPT (F10-Brooks)
   Question: Is the concept clear and compelling?

   PRELIMINARY ASSESSMENT (from premise):
   ✓ HIGH CONCEPT: Yes - "adopted princess discovers enemy kingdom heritage"
   ✓ STAKES CLEAR: Personal (identity) + External (prevent war)
   ✓ INHERENT CONFLICT: Loyalty torn between two kingdoms

   POTENTIAL CONCERNS:
   ⚠️ Trope familiarity: "secret heritage" is common YA fantasy

   TO VERIFY:
   [ ] What makes THIS "adopted heir" story unique vs others? (execution twist?)
   [ ] Can you pitch it in one sentence that feels fresh?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. CHARACTER (F8-Reedsy + F10-Brooks)
   Question: Are character arcs present and complete?

   PROTAGONIST - Princess (unnamed):

   WANT vs NEED Analysis (F8):
   [ ] WANT: Prevent war? Discover truth? Claim inheritance? (CLARIFY)
   [ ] NEED: What deeper transformation? (ex: learn to trust own judgment vs
       relying on authority? Accept dual identity?)

   FLAWS (F8 + F21-P4):
   [ ] What are her genuine psychological flaws? (Not just "impulsive" or "stubborn")
   [ ] Does she fail meaningfully before succeeding?

   ANTAGONIST (F8 + F21-P5):
   [ ] Who is the antagonist? (The kidnapper? Kingdom leaders? Conspiracy members?)
   [ ] Do they get POV or dimensional development? (F21-P5: TitaniaBlesh pattern)
   [ ] Can reader understand their motivations, even if disagree?

   TO VERIFY:
   [ ] Does protagonist change from ch 1 to final chapter? (Not just situation, but her as person)
   [ ] Can you articulate the transformation in one sentence?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. THEME (F10-Brooks)
   Question: Is theme integrated without being preachy?

   POTENTIAL THEMES (inferred):
   - Identity (nature vs nurture)
   - Loyalty (chosen family vs blood family)
   - Peace vs vengeance

   TO VERIFY:
   [ ] Do you consciously explore these themes through character choices?
   [ ] Or is theme accidental/unexamined?
   [ ] Does protagonist explicitly state theme in dialogue? (AVOID - show through action)

   INTEGRATION CHECK:
   [ ] Theme emerges from character decisions, not author intrusion?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. STORY STRUCTURE (F3-7Frameworks + F10-Brooks)
   Question: Is story structure sound (all required beats present)?

   IDENTIFY YOUR FRAMEWORK (F3):
   Based on premise, likely using: Hero's Journey OR Three-Act Structure

   THREE-ACT CHECK:
   [ ] ACT 1 (25%): Setup, Ordinary World, Inciting Incident (discovery of adoption?)
   [ ] ACT 2A (25%): Rising action, new world exploration (enemy kingdom?)
   [ ] ACT 2B (25%): Midpoint shift (passive→active), complications deepen
   [ ] ACT 3 (25%): Climax (war prevented?), resolution, transformation

   CRITICAL BEATS TO VERIFY (provide chapter numbers):
   [ ] Inciting Incident: When does she discover adoption? Ch___
   [ ] Point of No Return: When can't go back to old life? Ch___
   [ ] Midpoint: What's the major revelation/shift? Ch___
   [ ] All Is Lost: When does plan fail completely? Ch___
   [ ] Climax: Final confrontation? Ch___

   WEILAND ACT 2 CHECK (F11):
   [ ] Is Act 2 TRANSFORMATION (character actively changing) or FILLER (waiting for Act 3)?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. SCENE CONSTRUCTION (F11-Weiland + F10-Brooks)
   Question: Is scene construction effective (goal-conflict-outcome)?

   SCENE FORMULA (for each scene):
   GOAL: What does POV character want this scene?
   CONFLICT: What prevents them getting it?
   OUTCOME: Do they get it? (Usually: no, but worse / yes, but complicates)

   SAMPLE SCENE AUDIT (pick 3 random scenes):
   Scene 1 (Ch___, page___):
   [ ] Clear goal? [ ] Obstacle? [ ] Changed situation by scene end?

   Scene 2 (Ch___, page___):
   [ ] Clear goal? [ ] Obstacle? [ ] Changed situation by scene end?

   Scene 3 (Ch___, page___):
   [ ] Clear goal? [ ] Obstacle? [ ] Changed situation by scene end?

   RED FLAG SCENES (lacking goal-conflict-outcome):
   [ ] Identify any "nothing happens" scenes → CUT or ADD conflict

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. WRITING VOICE (F9-ElementsOfStyle + F10-Brooks)
   Question: Is writing voice consistent?

   VOICE CONSISTENCY CHECK:
   [ ] Does voice shift between chapters? (Unless intentional POV change)
   [ ] Tense consistency? (Past or present, not both unless flashback)
   [ ] POV consistency? (3rd limited? 1st? Don't head-hop)

   STYLE MARKERS (F9):
   [ ] Active vs passive voice: Mostly active? (YA fantasy should favor active)
   [ ] Sentence variety: Mix of short punchy + longer flowing?
   [ ] Dialogue tags: Simple "said" or over-rely on adverbs ("whispered urgently")?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. PACING (F5-6-7)
   Question: Is pacing varied appropriately for genre?

   YA FANTASY PACING EXPECTATIONS (F6-genre):
   - Faster than adult fantasy (readers expect quicker plot movement)
   - Action sequences frequent
   - Worldbuilding integrated, not info-dump chapters

   TO VERIFY:
   [ ] First 3 chapters: Does action start by ch 3? (YA readers drop fast)
   [ ] Middle (Act 2): Any "saggy middle" chapters? (all setup, no payoff)
   [ ] Climax: Is climax concentrated or spread over too many chapters?

   SENTENCE-LEVEL (F5):
   [ ] Vary sentence length for rhythm?
   [ ] Action scenes = shorter sentences?
   [ ] Emotional scenes = mix of short (impact) + long (introspection)?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. PLOT HOLES (F1-2)
   Question: Are plot holes resolved or intentional mysteries?

   CHARACTER CONSISTENCY (F1):
   [ ] Does protagonist act consistently with established personality?
   [ ] Any sudden skill appearances? (Fighting, magic, knowledge without setup)

   LOGICAL CONSISTENCY (F2):
   [ ] Magic system rules: Established and followed?
   [ ] Kingdom geography: Consistent travel times?
   [ ] Character motivations: Do antagonists act logically given their goals?

   TIMELINE:
   [ ] How much story time passes? (Days? Months?)
   [ ] Any timeline contradictions? (Events out of order, impossible timing)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY - PRIORITY ACTIONS:

HIGH PRIORITY (address before beta readers):
1. [ ] Complete Want/Need analysis for protagonist (affects entire arc)
2. [ ] Verify all required structural beats present (Act 2 most likely weak point)
3. [ ] Audit Act 2 for transformation vs filler (F11-Weiland)
4. [ ] Check first 3 chapters for fast hook (YA pacing requirement)

MEDIUM PRIORITY (second draft):
5. [ ] Scene-by-scene goal-conflict-outcome audit
6. [ ] Character consistency pass (F1)
7. [ ] Magic system logic check (F2)
8. [ ] POV/tense consistency

LOW PRIORITY (polish phase):
9. [ ] Sentence variety for rhythm (F5)
10. [ ] Dialogue tag simplification (F9)

NEXT STEPS:
1. Answer the clarifying questions above (Want/Need, antagonist, theme)
2. Provide specific scenes/chapters for detailed analysis
3. Once structure validated, move to sentence-level editing

Want me to deep-dive any specific competency? (ex: "Analyze structure in detail"
or "Help me with character Want/Need")
```

---

## 🎯 Tips for Best Results

### 1. Be Specific About Genre
**Why**: Fantasy has different rules than literary fiction
```
✓ GOOD: "Genre: Grimdark Fantasy, tone: dark, morally gray characters"
✗ VAGUE: "It's fantasy"
```

### 2. Provide Context
**Why**: Helps agent give genre-appropriate advice
```
✓ GOOD: "This is chapter 7 of 25. Protagonist just discovered betrayal in ch 6."
✗ MINIMAL: "Check this scene"
```

### 3. State Your Specific Concern
**Why**: Focuses analysis on what matters to you
```
✓ GOOD: "I'm worried the pacing drags in the middle. Can you analyze?"
✗ VAGUE: "What's wrong with this?"
```

### 4. Include Word Count for Context
**Why**: Helps assess if content is appropriate length
```
✓ GOOD: "Scene: 2500 words. Feels slow?"
✗ MISSING: [Pastes scene without context]
```

### 5. Ask About Limitations
**Why**: Agent has documented gaps (brainstorming, quantitative metrics)
```
✓ GOOD: "I know brainstorming is limited (Gap7). What CAN you help with?"
```

---

## ⚠️ Known Limitations (Agent Will Disclose These)

### Limited Capabilities:
1. **Brainstorming Analysis (Gap 7)**: Can assess quantity/diversity/novelty/feasibility, but lacks structured frameworks like Design Thinking
2. **Quantitative Metrics (Gap 2, 6)**: Without text samples, cannot provide precise stats like "average 18 words/sentence"
3. **Save the Cat Details (Gap 3)**: Overview only, detailed 15-beat mechanics need Jessica Brody's book
4. **Sanderson Specifics (Gap 4)**: General principles only, detailed lectures need BYU YouTube access

### When Agent Says "Limited":
This is TRANSPARENCY, not failure. Agent will:
- Explain what it CAN do
- Offer alternative approaches
- Cite which Gap applies

---

## 🔄 Workflow Examples

### Scenario A: New Manuscript (Plotting Stage)
```
Session 1: "Help me use Snowflake Method (F4) to develop my premise"
Session 2: "Check my character Want/Need alignment (F8)"
Session 3: "Which story structure framework fits my plot? (F3)"
```

### Scenario B: First Draft Complete (Revision)
```
Session 1: "Run developmental editing checklist on my manuscript"
Session 2: "Deep dive character consistency - I think protagonist acts out of character in ch 12"
Session 3: "Analyze pacing for entire Act 2 (chapters 8-15)"
```

### Scenario C: Specific Problem (Troubleshooting)
```
Problem: "Readers say my worldbuilding is info-dumpy"
Agent Analysis: Uses F21-P2 (Silent Worldbuilding) + F6 (Pacing-Structural)
Solution: Convert exposition to dialogue/action, apply Titania Blesh pattern
```

---

## 📊 Interpreting Confidence Levels

Agent always provides confidence scores. Here's what they mean:

### HIGH Confidence
- Based on **multiple independent sources**
- Technique widely recognized
- Example: Character Consistency Framework (F1 - The Write Practice + Reedsy cross-reference)
- **Trust Level**: Apply recommendation with confidence

### MEDIUM Confidence
- Based on **single authoritative source** OR **multiple reader observations**
- Example: Titania Blesh patterns (15+ reviews using consistent terminology)
- **Trust Level**: Strong recommendation, but consider your specific context

### LOW Confidence
- Single limited source OR subjective interpretation OR documented gap area
- Agent will note this explicitly
- **Trust Level**: Consider as option, not requirement

---

## 🆘 Troubleshooting

### Problem: "Agent doesn't stay in character"
**Solution**:
- Option 1: Re-paste TOON file and add: `Stay in character as Aria throughout this conversation`
- Option 2: When it breaks character, say: `Return to Aria mode`

### Problem: "Recommendations seem generic"
**Solution**: Provide more context
```
Instead of: "Check this scene"
Try: "This is chapter 5 (of 20), fantasy, after protagonist discovers betrayal.
Check for pacing issues and character consistency with earlier chapters."
```

### Problem: "I don't understand a citation (e.g., 'F7-Mythcreants')"
**Ask**: `Explain what F7-Mythcreants means`
**Agent will respond**: "Finding 7 from research: Dialogue Pacing techniques from Mythcreants
(authoritative craft blog). Covers fast dialogue (creates tension) vs slow dialogue (reduces tension)."

### Problem: "Agent says capability is 'LIMITED'"
**This is normal**: Agent has documented gaps
**Ask**: `What CAN you do for [topic] given the limitation?`
**Agent will**: Explain available options within limitations

---

## 💬 Conversation Starters

Copy/paste these to start sessions:

### General Analysis:
```
I have a [genre] manuscript, [word count]. I need help with [specific issue].
Here's the context: [summary]. Can you analyze?
```

### Plot Holes:
```
Analyze this for plot holes using the Character Consistency Framework (F1):
[paste scene or describe situation]
Genre: [fantasy/scifi/romantasy/literary]
```

### Pacing:
```
This chapter feels [slow/fast/uneven]. Analyze pacing using sentence structure
and dialogue techniques (F5-6-7):
[paste chapter or excerpt]
Genre: [genre]
Chapter position: [X of Y total]
```

### Style Replication:
```
I want to write with a style similar to [author name]. What patterns should I apply?
Genre: [genre]
Current manuscript: [brief description]
```

### Structure:
```
Check my story structure. I think I'm using [framework name, or "not sure"]:
[Provide: premise, major plot points, or chapter breakdown]
Genre: [genre]
```

### Developmental Checklist:
```
Run the 8-point developmental editing checklist (Brooks + Weiland + Penn):
Manuscript: [title]
Genre: [genre]
Word count: [count]
Status: [first draft / revised / beta feedback received]
Premise: [1-2 sentence summary]
```

---

## 📚 Reference - Finding Numbers Quick Guide

When agent cites "F#", here's what it means:

- **F1**: Plot Holes - Character Consistency (The Write Practice)
- **F2**: Plot Holes - Resolution Strategies (TCK Publishing)
- **F3**: 7 Story Structure Frameworks (Reedsy)
- **F4**: Snowflake Method (Randy Ingermanson)
- **F5**: Pacing - Sentence Structure (The Write Practice)
- **F6**: Pacing - Structural Indicators (Reedsy)
- **F7**: Pacing - Dialogue Techniques (Mythcreants)
- **F8**: Character Development - Wants/Needs (Reedsy)
- **F9**: Style - Elements of Style (Strunk & White via The Write Practice)
- **F10**: Brooks 6 Competencies (Story Engineering)
- **F11-12**: Weiland Story Structure (Helping Writers Become Authors)
- **F13**: Penn Workflows - Plotter vs Pantser (The Creative Penn)
- **F14**: Writing Excuses Craft Topics (Sanderson/Kowal/Wells)
- **F15**: Mythcreants Plot & Character (Mythcreants blog)
- **F16**: Friedman Cinematic Techniques (Jane Friedman)
- **F17-20**: Various Craft Resources (SFWA, Grammar Girl, BookFox, Writing-World)
- **F21**: Titania Blesh 8 Patterns (Goodreads/Audible - 15+ reviews)

**Gap 1-7**: Known research limitations (agent will disclose when relevant)

---

## ✅ Success Checklist

Before ending a session, verify:

- [ ] Agent provided specific recommendations (not vague "make it better")
- [ ] Each recommendation cited a Finding (F#) or disclosed a Gap
- [ ] Confidence level stated (HIGH/MED/LOW) with justification
- [ ] Genre-specific guidance applied (fantasy ≠ literary)
- [ ] Actionable next steps provided (checkboxes or numbered list)
- [ ] If limitation mentioned, alternative approach offered

---

## 🎓 Learning Mode

Want to learn the craft techniques, not just get fixes?

**Ask**: `Teach me about [technique] (F#) so I can apply it myself`

**Example**:
```
User: "Teach me F7 (Dialogue Pacing) so I can analyze my own scenes"

Agent Response: [Provides detailed explanation of fast vs slow dialogue techniques,
with examples, metrics to measure, and practice exercises]
```

---

## 📞 Getting Help

### If Agent Seems Confused:
1. Restate using Finding numbers: "Analyze using F1 (plot holes)" instead of "check for problems"
2. Provide genre context explicitly
3. Break complex requests into steps

### If You're Confused by Agent Output:
1. Ask: `Explain [term] in simpler terms`
2. Ask: `Give me an example from a published book`
3. Ask: `What's the most important thing to fix first?`

### If You Want Different Approach:
1. Say: `That recommendation doesn't fit my story because [reason]. Alternative?`
2. Agent will: Suggest different technique from research base

---

## 🚀 Ready to Start?

1. **Load agent** (see "How to Load" section above)
2. **Confirm activation**: Agent responds with greeting as "Aria"
3. **Start with**: Genre + what you need help with
4. **Provide context**: Chapter numbers, word counts, specific concerns
5. **Review output**: Check for F# citations, confidence levels, actionable steps
6. **Iterate**: Ask follow-ups, request clarification, dive deeper

**First session suggestion**:
```
I'm writing a [genre] novel. Can you introduce yourself and explain what
you can help me with? What information do you need from me to provide
the best analysis?
```

Agent will guide you from there!

---

**Version**: 1.0
**Last Updated**: 2025-12-30
**Agent File**: `agents/novel-editor-chatgpt-toon.txt`
**Research Base**: 21 Findings, 24 Sources, 9.5/10 Quality Score
