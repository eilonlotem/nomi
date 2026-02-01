# Quick Reference: Human-Like AI Responses

## What Changed?

Mock users now chat more naturally, like real people, not robots.

## Core Principles

### ✓ DO
- Use contractions (I'm, can't, you're)
- Keep responses SHORT (1-2 sentences)
- Ask follow-up questions
- Show personality and emotions
- Use emojis sparingly (1-2 max)
- Remember conversation context
- Respond in user's language (Hebrew for Hebrew profiles)
- Allow minor imperfections
- Share brief personal stories

### ✗ DON'T
- Write essay-length responses
- Be overly formal or polite
- Use perfect grammar always
- Overuse emojis
- Give therapy-like responses
- Break character (never mention being AI)
- Suggest meeting up (too early)
- Repeat same phrases

## Key Files

| File | Purpose |
|------|---------|
| `backend/matching/ai_service.py` | Main AI response generation logic |
| `backend/HUMAN_LIKE_AI_IMPROVEMENTS.md` | Full technical documentation |
| `backend/matching/test_human_responses.py` | Test suite |
| `MOCK_USER_IMPROVEMENTS_SUMMARY.md` | Executive summary |
| `RESPONSE_EXAMPLES.md` | Before/after examples |

## Testing

```bash
# Run automated tests
cd backend
source venv/bin/activate
python matching/test_human_responses.py
```

## Configuration

Located in `backend/matching/ai_service.py`:

```python
class AIConfig:
    temperature: 0.9          # Creativity level (0.0-2.0)
    presence_penalty: 0.6     # Topic variety
    frequency_penalty: 0.3    # Reduce repetition
```

**Adjust temperature**:
- Higher (1.0+) = more creative/varied
- Lower (0.7-) = more focused/consistent

## Language Support

The system auto-detects language from profile bio:

| Language | Detection | Status |
|----------|-----------|--------|
| Hebrew | Hebrew characters (U+0590-U+05FF) | ✅ Supported |
| Arabic | Arabic characters (U+0600-U+06FF) | ✅ Supported |
| English | Default fallback | ✅ Supported |
| Spanish | Via user preference | ✅ Supported |
| French | Via user preference | ✅ Supported |

## Troubleshooting

### Problem: Responses too long
**Solution**: Responses are optimized for 1-2 sentences, but if still too long, check `max_tokens` in `AIConfig` (currently 150)

### Problem: Too formal/robotic
**Solution**: Already addressed! System prompt emphasizes casual, natural language. If issue persists, review the prompt in `PersonalityPromptBuilder.build()`

### Problem: Wrong language
**Solution**: Check profile's bio language. System detects Hebrew/Arabic from bio text. Can also set `user.preferred_language`

### Problem: Too repetitive
**Solution**: `frequency_penalty: 0.3` reduces repetition. Can increase up to 1.0 if needed

### Problem: Not enough personality
**Solution**: `temperature: 0.9` allows creativity. Profile bios should be detailed to give AI more personality context

## Response Style Examples

**Good responses:**
```
hey! saw you're into photography too 📸
```
```
haha same here! coffee is basically my life
```
```
that's so cool! tell me more
```
```
ממש! יש לנו המון מה לדבר 😊
```

**Bad responses (old style):**
```
Hello! That is very interesting. I would love to hear more about your hobbies and interests.
```

## Monitoring

Track these metrics:
- Average conversation length (messages per conversation)
- Response rate (users replying to mock users)
- Engagement time
- User feedback on naturalness

## Quick Wins

1. ✅ **More casual tone** - Contractions, informal language
2. ✅ **Shorter responses** - 1-2 sentences vs paragraphs
3. ✅ **Better variety** - No repetitive patterns
4. ✅ **Language support** - Hebrew/Arabic responses
5. ✅ **Context retention** - Remembers earlier messages
6. ✅ **Personality** - Each mock user feels unique

## Need More Help?

- Read `MOCK_USER_IMPROVEMENTS_SUMMARY.md` for full context
- Check `RESPONSE_EXAMPLES.md` for before/after comparisons
- Review `backend/HUMAN_LIKE_AI_IMPROVEMENTS.md` for technical details
- Run `test_human_responses.py` to validate changes

---

**Updated**: February 2, 2026  
**Version**: 2.0 (Human-Like Responses)
