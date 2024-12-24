from ..models import ImageAnalysisResult, ProductDescription
import random

class DescriptionGenerator:
    def __init__(self):
        self.templates = {
            "professional": [
                "Experience our {quality} {main_object}. This {style} {colors} design delivers exceptional performance.",
                "Introducing our {quality} {main_object}. A {style} solution in {colors}.",
                "Discover our {quality} {main_object}. {style} craftsmanship in {colors}."
            ],
            "casual": [
                "Meet our amazing {colors} {main_object}! A {quality} {style} solution.",
                "Check out this {quality} {colors} {main_object}. {style} design at its best.",
                "Get our {quality} {main_object} in {colors}. Pure {style} excellence."
            ],
            "luxury": [
                "Indulge in our {quality} {main_object}. Masterfully crafted in {colors}, {style} elegance.",
                "Experience our {quality} {main_object}. {style} sophistication in {colors}.",
                "Elevate with our {quality} {main_object}. {style} refinement in {colors}."
            ],
            "technical": [
                "{quality} {main_object}. {style} engineering, {colors} finish.",
                "Advanced {main_object}. {quality} build, {colors} exterior, {style} design.",
                "{quality} {main_object}. {colors} chassis, {style} performance."
            ]
        }

    def _format_colors(self, colors: list) -> str:
        if len(colors) == 1:
            return colors[0]
        return " and ".join(colors)

    async def generate_description(self, analysis: ImageAnalysisResult, tone: str = "professional") -> ProductDescription:
        try:
            main_object = analysis.objects[0]
            colors_text = self._format_colors(analysis.colors)

            # Select a random template for the chosen tone
            templates = self.templates.get(tone, self.templates["professional"])
            template = random.choice(templates)

            description = template.format(
                main_object=main_object,
                colors=colors_text,
                style=analysis.style,
                quality=analysis.quality
            )

            # Generate highlights
            highlights = [
                f"{analysis.quality} {main_object}",
                f"{colors_text} design",
                f"{analysis.style} build"
            ]

            return ProductDescription(
                generated_description=description,
                highlights=highlights,
                suggested_price_range="Premium Product"
            )

        except Exception as e:
            print(f"Error in generate_description: {str(e)}")
            return ProductDescription(
                generated_description="Error generating description",
                highlights=["Error processing request"],
                suggested_price_range="Not available"
            )