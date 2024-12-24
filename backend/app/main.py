from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .services.vision import VisionAPI
from .services.description import DescriptionGenerator

app = FastAPI(title="Product Description Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
vision_service = VisionAPI()
description_service = DescriptionGenerator()

@app.post("/generate-single")
async def generate_single_description(
    image: UploadFile,
    tone: str = "professional"
):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await image.read()
    analysis = await vision_service.analyze_image(image_bytes)
    return await description_service.generate_description(analysis, tone)

@app.post("/generate-multiple")
async def generate_multiple_descriptions(
    images: List[UploadFile],
    tone: str = "professional"
):
    if not all(image.content_type.startswith('image/') for image in images):
        raise HTTPException(status_code=400, detail="All files must be images")
    
    results = []
    for image in images:
        image_bytes = await image.read()
        analysis = await vision_service.analyze_image(image_bytes)
        description = await description_service.generate_description(analysis, tone)
        results.append(description)
    
    return results