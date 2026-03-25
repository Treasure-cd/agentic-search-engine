from __future__ import annotations

from pathlib import Path
from typing import Any
import re

import yaml


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$", re.MULTILINE)


class SkillParser:
    """
    Parse SKILL.md/Skills.md inputs into a normalized record for indexing.
    """

    @staticmethod
    def parse_skill_md(file_path: str) -> dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found at {file_path}")

        content = path.read_text(encoding="utf-8", errors="replace")
        parsed = SkillParser.parse_skill_content(content)
        parsed["source_path"] = str(path)
        return parsed

    @staticmethod
    def parse_skill_content(content: str) -> dict[str, Any]:
        frontmatter: dict[str, Any] = {}
        body = content

        match = _FRONTMATTER_RE.match(content)
        if match:
            try:
                loaded = yaml.safe_load(match.group(1))
                if isinstance(loaded, dict):
                    frontmatter = loaded
            except yaml.YAMLError:
                # Keep parsing body even with malformed frontmatter.
                frontmatter = {}
            body = content[match.end() :]

        title = SkillParser._as_str(
            frontmatter.get("title")
            or frontmatter.get("name")
            or frontmatter.get("skill")
            or SkillParser._first_heading(body)
        )

        tags = SkillParser._normalize_tags(
            frontmatter.get("tags") or frontmatter.get("keywords")
        )

        bullets = [b.strip() for b in _BULLET_RE.findall(body) if b.strip()]
        body_text = SkillParser._flatten_markdown(body)

        summary_parts = []
        if title:
            summary_parts.append(f"Skill: {title}")
        if tags:
            summary_parts.append(f"Tags: {', '.join(tags)}")
        if bullets:
            summary_parts.append("Capabilities: " + "; ".join(bullets[:12]))
        elif body_text:
            summary_parts.append(body_text[:2000])

        normalized_text = "\n".join(summary_parts).strip()
        if not normalized_text:
            normalized_text = "Skill file has no parseable capability text."

        return {
            "skill_name": title or None,
            "tags": tags,
            "metadata": frontmatter,
            "normalized_text": normalized_text,
            "raw_excerpt": body_text[:1000],
        }

    @staticmethod
    def _normalize_tags(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, list):
            out: list[str] = []
            for item in value:
                if isinstance(item, str):
                    item = item.strip()
                    if item:
                        out.append(item)
            return out
        return []

    @staticmethod
    def _first_heading(text: str) -> str:
        m = _HEADING_RE.search(text)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _flatten_markdown(text: str) -> str:
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`[^`]+`", " ", text)
        text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
        text = re.sub(r"[#>*_~\-]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def _as_str(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""
