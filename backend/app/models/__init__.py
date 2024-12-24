from pydantic import BaseModel
from typing import List, Optional

class ImageAnalysisResult(BaseModel):
    objects: List[str]
    colors: List[str]
    style: str
    quality: str
    background: str

class ProductDescription(BaseModel):
    generated_description: str
    highlights: List[str]
    suggested_price_range: Optional[str] = None
    original_description: Optional[str] = None