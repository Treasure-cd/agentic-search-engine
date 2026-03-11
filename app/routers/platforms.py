from typing import Any
from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import select
from app.core.deps import SessionDep
from app.models.database import Platform, SkillEmbedding
from app.schemas.requests import PlatformCreate
from app.services.crawler import CrawlerService
from app.services.vectorizer import Vectorizer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/platforms", tags=["platforms"])

async def background_crawl_task(platform_id: str, url: str):
    """
    Crawls the platform, generating a fallback description and scanning for skills.
    If a skill is found, it automatically gets indexed.
    """
    crawler = CrawlerService()
    try:
        # We need a new session context for background tasks
        from app.db.session import SessionLocal
        import uuid
        async with SessionLocal() as session:
            platform_uuid = uuid.UUID(platform_id)
            result = await session.execute(select(Platform).filter(Platform.id == platform_uuid))
            platform = result.scalars().first()
            if not platform:
                return

            crawl_result = await crawler.crawl_platform(url)
            
            # Auto-update description if not explicitly provided
            if not platform.description and crawl_result["description"]:
                platform.description = crawl_result["description"]
            
            if crawl_result["skill_content"]:
                # Initialize the Vectorizer and auto-ingest the discovered skill
                logger.info(f"Discovered skill for platform {url}, auto-indexing.")
                vectorizer = Vectorizer()
                embedding = vectorizer.generate_embeddings([crawl_result["skill_content"]])[0]
                
                db_skill = SkillEmbedding(
                    platform_id=platform.id,
                    dimension=embedding,
                    capabilities=crawl_result["skill_content"]
                )
                session.add(db_skill)
            
            await session.commit()
    except Exception as e:
        logger.error(f"Error during background crawl of {url}: {e}")
    finally:
        await crawler.close()


@router.post("/")
async def create_platform(
    platform_in: PlatformCreate,
    session: SessionDep,
    background_tasks: BackgroundTasks
) -> dict[str, Any]:
    """
    Submit a new platform to the index. Kicks off an asynchronous background 
    task to generate descriptions and discover AI skills.
    """
    db_platform = Platform(
        name=platform_in.name,
        url=str(platform_in.url),
        homepage_uri=str(platform_in.homepage_uri),
        description=platform_in.description
    )
    session.add(db_platform)
    await session.commit()
    await session.refresh(db_platform)

    # Queue the background crawl task
    background_tasks.add_task(background_crawl_task, str(db_platform.id), str(db_platform.url))

    return {
        "id": str(db_platform.id),
        "name": db_platform.name,
        "message": "Platform created successfully. Crawler dispatched to discover skills and analyze the webpage."
    }
