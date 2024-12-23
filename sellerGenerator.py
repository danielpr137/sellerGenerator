# main.py
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import aiohttp
import asyncio
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Product Description Generator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageAnalysisResult(BaseModel):
    objects: List[str]
    colors: List[str]
    style: str
    quality: str
    background: str

class ProductDescription(BaseModel):
    original_description: Optional[str]
    generated_description: str
    highlights: List[str]
    suggested_price_range: Optional[str]

class VisionAPI:
    def __init__(self):
        self.api_key = os.getenv("VISION_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def analyze_image(self, image: bytes) -> ImageAnalysisResult:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Convert image to base64
            import base64
            image_base64 = base64.b64encode(image).decode('utf-8')
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this product image and provide details about: objects, colors, style, quality, and background. Return in a structured format."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }

            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Vision API error")
                result = await response.json()
                # Parse the response and create ImageAnalysisResult
                # This is a simplified version - you'd need to parse the actual response
                return ImageAnalysisResult(
                    objects=["sample"],
                    colors=["sample"],
                    style="sample",
                    quality="sample",
                    background="sample"
                )

class DescriptionGenerator:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def generate_description(self, analysis: ImageAnalysisResult, tone: str = "professional") -> ProductDescription:
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }

            prompt = f"""
            Create a compelling product description based on the following analysis:
            Objects: {', '.join(analysis.objects)}
            Colors: {', '.join(analysis.colors)}
            Style: {analysis.style}
            Quality: {analysis.quality}
            Background: {analysis.background}
            
            Tone: {tone}
            
            Generate a description that highlights the key features and benefits.
            """

            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "claude-3-opus-20240229",
                "max_tokens": 500
            }

            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Description generation error")
                result = await response.json()
                # Parse the response and create ProductDescription
                return ProductDescription(
                    generated_description="Sample description",
                    highlights=["Sample highlight"],
                    suggested_price_range="$XX-$YY"
                )

class ProductDescriptionAgent:
    def __init__(self):
        self.vision_api = VisionAPI()
        self.description_generator = DescriptionGenerator()

    async def process_image(self, image: bytes, tone: str = "professional") -> ProductDescription:
        analysis = await self.vision_api.analyze_image(image)
        description = await self.description_generator.generate_description(analysis, tone)
        return description

    async def process_multiple_images(
        self, 
        images: List[bytes], 
        tone: str = "professional"
    ) -> List[ProductDescription]:
        tasks = [self.process_image(image, tone) for image in images]
        return await asyncio.gather(*tasks)

# API Routes
@app.post("/generate-single", response_model=ProductDescription)
async def generate_single_description(
    image: UploadFile,
    tone: str = "professional"
):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await image.read()
    agent = ProductDescriptionAgent()
    return await agent.process_image(image_bytes, tone)

@app.post("/generate-multiple", response_model=List[ProductDescription])
async def generate_multiple_descriptions(
    images: List[UploadFile],
    tone: str = "professional"
):
    if not all(image.content_type.startswith('image/') for image in images):
        raise HTTPException(status_code=400, detail="All files must be images")
    
    image_bytes_list = [await image.read() for image in images]
    agent = ProductDescriptionAgent()
    return await agent.process_multiple_images(image_bytes_list, tone)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0000", port=8000)