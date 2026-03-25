from app.ingestion.skills_parser import SkillParser


def test_parse_skill_content_with_frontmatter_and_bullets():
    content = """---
name: Notifications
keywords: [email, alerts]
---
# Notifications Skill
- Send email alerts
- Trigger webhooks
"""

    parsed = SkillParser.parse_skill_content(content)

    assert parsed["skill_name"] == "Notifications"
    assert parsed["tags"] == ["email", "alerts"]
    assert "Send email alerts" in parsed["normalized_text"]
