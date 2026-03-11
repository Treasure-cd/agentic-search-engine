from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional

class PlatformCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    url: HttpUrl
    homepage_uri: HttpUrl
    description: Optional[str] = None

class SkillCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    platform_id: str
    capabilities: str
