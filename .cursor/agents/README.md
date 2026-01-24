---
name: README
model: gpt-5.2
---

# Nomi Cursor Agents

This directory contains specialized Cursor AI agents for different domains of the Nomi project.

## Available Agents

### 🧡 About Us Agent (`about-us.md`)
**Domain**: Public-facing marketing pages and content

**Responsibilities**:
- Managing `frontend/public/about.html` and related pages
- Brand voice and messaging consistency
- Hebrew/RTL content management
- Marketing content updates
- Accessibility compliance for public pages

**Use When**: Working on the About Us page, landing pages, privacy policy, terms of service, or any public-facing marketing content.

## How to Use Agents

### In Cursor Chat
Reference the agent by mentioning its domain:
- "As the About Us agent, update the hero section..."
- "Using the about-us agent rules, add a new testimonial section..."

### Creating New Agents
1. Create a new `.md` file in this directory
2. Define the agent's domain, responsibilities, and guidelines
3. Include relevant context about the codebase section
4. Add quality checklists and common tasks

## Agent Structure Template

```markdown
# [Agent Name]

You are **Nomi's [Domain] Agent** - a specialized assistant for [domain description].

## Your Domain
[List of files and areas this agent owns]

## Context & Knowledge
[Domain-specific knowledge the agent needs]

## Responsibilities
[What this agent should do]

## Guidelines
[How the agent should work]

## Quality Checklist
[Verification steps before completing tasks]
```

## Future Agents (Planned)

- **Matching Agent** - Algorithm and compatibility scoring
- **Chat Agent** - Messaging and conversation features
- **Profile Agent** - User profile and onboarding
- **Accessibility Agent** - WCAG compliance and a11y testing
- **i18n Agent** - Translations and localization
