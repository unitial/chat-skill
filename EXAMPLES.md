# Usage Examples

This document provides detailed examples of using the Chat Skills Runtime.

## Example 1: PDF Summary with Skill

**User Request:**
```
"I have a 50-page research paper on climate change. Can you help me create a structured summary?"
```

**What Happens:**

1. **Router Phase:**
   - Router analyzes the request
   - Identifies keywords: "structured summary", "paper"
   - Matches against skills
   - Decision: Use "PDF Summary" skill

2. **Chat Phase:**
   - System injects PDF Summary skill content
   - Chat agent follows the structured format from the skill
   - Generates response with proper sections:
     - Document Overview
     - Executive Summary
     - Key Sections
     - Important Data
     - Conclusions

**Expected Output Structure:**
```markdown
# PDF Summary: [Document Title]

**Type**: Research Paper
**Length**: 50 pages
**Topic**: Climate Change

## Executive Summary
[2-3 sentence overview]

## Key Sections
1. **Introduction**: [Summary]
2. **Methods**: [Summary]
...
```

## Example 2: Academic Paper Review

**User Request:**
```
"Can you review my paper titled 'Transformer Models for Sequential Data'? I'm submitting to NeurIPS."
```

**What Happens:**

1. **Router Phase:**
   - Keywords: "review my paper", "submitting"
   - Matches: "Paper Review" skill
   - Decision: Use Paper Review skill

2. **Chat Phase:**
   - Injects Paper Review skill template
   - Agent provides structured review with:
     - Paper Overview
     - Strengths (3-5 points)
     - Weaknesses (major and minor)
     - Section-by-section feedback
     - Technical correctness assessment
     - Originality & significance
     - Recommendation

**Expected Output:**
```markdown
## Paper Review: Transformer Models for Sequential Data

### Paper Overview
**Authors**: [To be provided]
**Venue**: NeurIPS
**Area**: Machine Learning

**Summary**: [3-4 sentence summary]

### Strengths
- **Clear motivation**: ...
- **Novel approach**: ...

### Weaknesses

#### Major Issues
- **Limited baselines**: ...

#### Minor Issues
- Figure 3 caption could be clearer
...

### Recommendation
**Rating**: Weak Accept
**Confidence**: High
**Justification**: ...
```

## Example 3: Course Outline Creation

**User Request:**
```
"I need to create a 10-week online course on Python for beginners."
```

**What Happens:**

1. **Router Phase:**
   - Keywords: "create", "course", "10-week"
   - Matches: "Course Outline" skill
   - Decision: Use Course Outline skill

2. **Chat Phase:**
   - Injects Course Outline skill
   - Agent creates structured course with:
     - Course header (title, duration, level)
     - Learning objectives
     - Week-by-week breakdown
     - Assessment strategy
     - Required materials

## Example 4: Regular Chat (No Skills)

**User Request:**
```
"Hi! How's the weather today?"
```

**What Happens:**

1. **Router Phase:**
   - Analyzes request
   - Identifies: casual conversation, no skill needed
   - Decision: No skills

2. **Chat Phase:**
   - Normal conversation
   - No skill injection
   - Direct response

**Output:**
```
I don't have access to real-time weather information, but I'd be happy to chat!
What would you like to talk about?
```

## Example 5: Multiple Skills

**User Request:**
```
"I need to review a research paper and then create a summary for non-experts."
```

**What Happens:**

1. **Router Phase:**
   - Keywords: "review", "paper", "summary"
   - Matches both: "Paper Review" AND "PDF Summary"
   - Decision: Use both skills (if within max_skills limit)

2. **Chat Phase:**
   - Injects BOTH skills
   - Agent can reference both frameworks
   - Provides comprehensive response combining:
     - Academic review elements
     - Summary structure for accessibility

## Tips for Effective Use

### 1. Be Specific in Requests

**Less Effective:**
```
"Help me with this paper"
```

**More Effective:**
```
"Can you review this computer science paper and provide structured feedback for revision?"
```

### 2. Mention Keywords

Skills trigger based on keywords. Include terms like:
- For PDF Summary: "summarize", "overview", "key points"
- For Paper Review: "review", "feedback", "critique"
- For Course Outline: "course", "curriculum", "syllabus"

### 3. Use --show-routing to Learn

Run with `--show-routing` to see which skills are selected:
```bash
chat-skills --skills-dir ./demo_skills --show-routing
```

This helps you understand what triggers skills.

### 4. Context Matters

The router considers conversation history. If you're already discussing papers,
asking "can you review it?" will likely trigger Paper Review.

### 5. Override When Needed

If the wrong skill is selected (or no skill when you want one), be more explicit:
```
"Please use a structured paper review format to analyze..."
```

## Troubleshooting Examples

### Router Not Selecting Skills

**Problem:** You want a skill but router doesn't select it.

**Solution:** Use more explicit keywords:
- Instead of: "What do you think about this paper?"
- Try: "Can you provide a structured academic review of this paper?"

### Wrong Skills Selected

**Problem:** Router selects irrelevant skills.

**Solution:**
- Reduce max_skills: `--max-skills 1`
- Be more specific in your request
- Consider improving skill descriptions in SKILL.md

### Skills Not Loading

**Problem:** "No skills found" warning.

**Solution:**
- Check directory exists: `ls -la ./demo_skills`
- Verify SKILL.md files exist: `find ./demo_skills -name "SKILL.md"`
- Use absolute path: `--skills-dir /full/path/to/skills`
