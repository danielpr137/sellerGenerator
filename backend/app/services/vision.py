import os
import aiohttp
import base64
import re
from dotenv import load_dotenv
from ..models import ImageAnalysisResult

load_dotenv()

class VisionAPI:
    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
        self.api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

    def _clean_caption(self, caption: str) -> str:
        # Remove common descriptive phrases
        phrases_to_remove = [
            'a close up of',
            'close up',
            'a picture of',
            'an image of',
            'a photo of',
            'there is',
            'this is',
            'we can see',
            'what appears to be',
            'appears to be',
            'it looks like',
            'on a desk',
            'on the desk',
            'on table',
            'on the table',
            'in the background',
            'in background',
            'a view of',
        ]
        
        # Convert to lowercase and remove phrases
        cleaned = caption.lower()
        for phrase in phrases_to_remove:
            cleaned = cleaned.replace(phrase, '')
            
        # Remove location prepositions
        location_patterns = r'\s+(on|in|at|by|near|beside|behind|under|over|above)\s+\w+'
        cleaned = re.sub(location_patterns, '', cleaned)
        
        # Remove articles and extra spaces
        cleaned = re.sub(r'\s+a\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+an\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+the\s+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

    def _identify_main_product(self, caption: str) -> tuple:
        quality_terms = ['premium', 'high-end', 'professional', 'quality', 'luxury']
        color_terms = ['black', 'white', 'silver', 'blue', 'red', 'transparent', 'clear', 'grey', 'gray', 'metallic']
        
        # Get words and remove common noise words
        words = caption.split()
        words = [w for w in words if w not in ['of', 'the', 'a', 'an', 'on', 'in', 'at', 'by', 'with']]
        
        # Get main product
        product_keywords = {
            'mouse': ['mouse', 'mice'],
            'keyboard': ['keyboard', 'keypad'],
            'monitor': ['monitor', 'display', 'screen'],
            'bottle': ['bottle', 'container'],
            'pen': ['pen', 'pencil', 'marker'],
            'headphones': ['headphones', 'headset', 'earphones']
        }
        
        # Find the product type
        product = None
        for prod_type, keywords in product_keywords.items():
            if any(keyword in words for keyword in keywords):
                product = prod_type
                break
        
        if not product:
            # If no specific product found, get the first noun-like word
            product = next((word for word in words if len(word) > 3 and word not in quality_terms + color_terms), 'product')
        
        # Find colors
        colors = [word for word in words if word in color_terms]
        if not colors:
            colors = ['black']  # Default color

        # Find quality indicators
        quality = 'Premium' if any(term in words for term in quality_terms) else 'Professional'
        
        # Extract features (excluding the product name and common words)
        features = [word for word in words 
                   if len(word) > 3 
                   and word not in quality_terms 
                   and word not in color_terms
                   and word != product]
        
        return product, features, colors, quality

    async def analyze_image(self, image_bytes: bytes) -> ImageAnalysisResult:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "inputs": base64.b64encode(image_bytes).decode('utf-8'),
                }

                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if not response.ok:
                        raise Exception(f"Hugging Face API error: {response.status}")
                    
                    result = await response.json()
                    raw_caption = result[0]['generated_text']
                    print(f"Raw caption: {raw_caption}")
                    
                    cleaned_caption = self._clean_caption(raw_caption)
                    print(f"Cleaned caption: {cleaned_caption}")

                    product, features, colors, quality = self._identify_main_product(cleaned_caption)
                    print(f"Identified: product={product}, features={features}, colors={colors}, quality={quality}")
                    
                    return ImageAnalysisResult(
                        objects=[product] + features,
                        colors=colors,
                        style="Professional",
                        quality=quality,
                        background="Product focused"
                    )

        except Exception as e:
            print(f"Error in analyze_image: {str(e)}")
            return ImageAnalysisResult(
                objects=["product"],
                colors=["black"],
                style="Professional",
                quality="Standard",
                background="Product focused"
            )