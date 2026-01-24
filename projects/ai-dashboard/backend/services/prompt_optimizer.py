# AI Dashboard - Prompt Optimizer using DSPy

import os
import logging
from typing import Optional
import dspy

logger = logging.getLogger(__name__)


class VideoScriptSignature(dspy.Signature):
    """Generate an engaging YouTube video script about an AI topic"""

    topic = dspy.InputField(desc="The AI topic or idea for the video")
    target_audience = dspy.InputField(desc="Target audience for the video", default="tech enthusiasts and developers")
    video_length = dspy.InputField(desc="Target video length in minutes", default="5-10")

    title = dspy.OutputField(desc="Catchy YouTube video title (max 100 chars)")
    description = dspy.OutputField(desc="YouTube video description with keywords (max 500 chars)")
    script = dspy.OutputField(desc="Full video script with intro, main content, and outro")
    tags = dspy.OutputField(desc="Comma-separated list of 10-15 relevant YouTube tags")
    thumbnail_prompt = dspy.OutputField(desc="DALL-E prompt for generating an eye-catching thumbnail")


class ContentEnhancer(dspy.Signature):
    """Enhance and improve content for better engagement"""

    original_content = dspy.InputField(desc="Original content to enhance")
    content_type = dspy.InputField(desc="Type of content: title, description, or script")
    style = dspy.InputField(desc="Desired style: professional, casual, educational, entertaining")

    enhanced_content = dspy.OutputField(desc="Enhanced version of the content")
    improvements_made = dspy.OutputField(desc="List of improvements made")


class PromptOptimizer:
    """Optimizes prompts for YouTube video content generation using DSPy"""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        if self.api_key:
            # Configure DSPy with Claude
            self.lm = dspy.Claude(
                model="claude-3-5-sonnet-20241022",
                api_key=self.api_key,
                max_tokens=4000
            )
            dspy.configure(lm=self.lm)

            # Create modules
            self.script_generator = dspy.ChainOfThought(VideoScriptSignature)
            self.content_enhancer = dspy.ChainOfThought(ContentEnhancer)
        else:
            logger.warning("ANTHROPIC_API_KEY not set - PromptOptimizer will be limited")
            self.lm = None

    def generate_video_content(
        self,
        topic: str,
        target_audience: str = "tech enthusiasts and developers",
        video_length: str = "5-10"
    ) -> dict:
        """
        Generate complete video content from a topic

        Args:
            topic: The AI topic for the video
            target_audience: Who the video is for
            video_length: Target length in minutes

        Returns:
            Dict with title, description, script, tags, thumbnail_prompt
        """
        if not self.lm:
            return self._fallback_generation(topic)

        try:
            result = self.script_generator(
                topic=topic,
                target_audience=target_audience,
                video_length=video_length
            )

            return {
                "title": result.title,
                "description": result.description,
                "script": result.script,
                "tags": [tag.strip() for tag in result.tags.split(",")],
                "thumbnail_prompt": result.thumbnail_prompt,
                "optimized": True
            }

        except Exception as e:
            logger.error(f"DSPy generation failed: {e}")
            return self._fallback_generation(topic)

    def enhance_content(
        self,
        content: str,
        content_type: str = "script",
        style: str = "educational"
    ) -> dict:
        """
        Enhance existing content for better engagement

        Args:
            content: Original content to enhance
            content_type: Type (title, description, script)
            style: Desired style

        Returns:
            Dict with enhanced content and improvements
        """
        if not self.lm:
            return {"enhanced_content": content, "improvements_made": []}

        try:
            result = self.content_enhancer(
                original_content=content,
                content_type=content_type,
                style=style
            )

            return {
                "enhanced_content": result.enhanced_content,
                "improvements_made": result.improvements_made.split("\n") if result.improvements_made else []
            }

        except Exception as e:
            logger.error(f"Content enhancement failed: {e}")
            return {"enhanced_content": content, "improvements_made": []}

    def optimize_prompt(self, user_prompt: str) -> str:
        """
        Optimize a user prompt for better AI generation

        Args:
            user_prompt: Raw user input

        Returns:
            Optimized prompt
        """
        # Apply prompt engineering best practices
        optimized = f"""You are creating content for a YouTube video about AI.

TOPIC: {user_prompt}

REQUIREMENTS:
- Make it engaging and accessible to a general tech audience
- Include practical examples and real-world applications
- Use a conversational but informative tone
- Structure content with clear intro, main points, and conclusion
- Include calls to action (subscribe, comment, like)

Please provide comprehensive, well-researched content that would work well for a 5-10 minute video."""

        return optimized

    def _fallback_generation(self, topic: str) -> dict:
        """Fallback when DSPy is not available"""
        return {
            "title": f"Understanding {topic}: A Complete Guide",
            "description": f"In this video, we explore {topic} and its applications in the AI world. Perfect for beginners and experts alike!",
            "script": f"Welcome to this video about {topic}. [Script needs to be generated with AI]",
            "tags": ["AI", "machine learning", "technology", "tutorial", topic.lower()],
            "thumbnail_prompt": f"Modern tech-style thumbnail about {topic}, blue and purple gradient, futuristic",
            "optimized": False
        }
