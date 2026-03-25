from __future__ import annotations

import hashlib
import logging
import os

from sqlalchemy import select

from app.db.session import SessionLocal
from app.ingestion.skills_parser import SkillParser
from app.models.database import Platform, SkillEmbedding
from app.services.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


async def ingest_skills_from_directory(directory: str) -> dict[str, int]:
    """
    Traverse a directory for SKILL.md/Skills.md, parse and index them.
    Redundant submissions are deduplicated by content hash per platform.
    """
    stats = {"processed": 0, "created": 0, "duplicates": 0, "failed": 0}

    async with SessionLocal() as session:
        parser = SkillParser()
        vectorizer = Vectorizer()

        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.lower() not in {"skill.md", "skills.md"}:
                    continue

                stats["processed"] += 1
                file_path = os.path.join(root, file_name)
                try:
                    parsed = parser.parse_skill_md(file_path)
                    capabilities = parsed["normalized_text"]
                    skill_name = parsed.get("skill_name")
                    tags = parsed.get("tags") or []

                    hash_source = f"{capabilities}|{skill_name}|{','.join(tags)}"
                    skill_hash = hashlib.sha256(hash_source.encode("utf-8")).hexdigest()

                    platform_name = skill_name or os.path.basename(root)

                    platform_result = await session.execute(
                        select(Platform).filter_by(name=platform_name)
                    )
                    platform = platform_result.scalars().first()
                    if not platform:
                        platform = Platform(name=platform_name, url="", homepage_uri="")
                        session.add(platform)
                        await session.commit()
                        await session.refresh(platform)

                    existing = await session.execute(
                        select(SkillEmbedding).filter(
                            SkillEmbedding.platform_id == platform.id,
                            SkillEmbedding.skill_hash == skill_hash,
                        )
                    )
                    if existing.scalars().first():
                        stats["duplicates"] += 1
                        continue

                    embedding = vectorizer.generate_embeddings([capabilities])[0]
                    session.add(
                        SkillEmbedding(
                            platform_id=platform.id,
                            dimension=embedding,
                            capabilities=capabilities,
                            skill_name=skill_name,
                            tags=tags,
                            skill_hash=skill_hash,
                        )
                    )
                    await session.commit()
                    stats["created"] += 1
                except Exception as e:
                    stats["failed"] += 1
                    logger.warning("Failed to process %s: %s", file_path, e)

    return stats
