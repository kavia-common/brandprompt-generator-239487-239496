"""
Pydantic models for the backend REST API.

These models validate frontend inputs (orientation/platform/brand/style) and define
stable, documented response shapes for the extension.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Orientation(str, Enum):
    """User intent / use-case for prompt generation."""

    post = "post"
    ad = "ad"
    email = "email"
    landing_page = "landing_page"
    other = "other"


class Platform(str, Enum):
    """Publishing platform / destination context."""

    instagram = "instagram"
    tiktok = "tiktok"
    facebook = "facebook"
    linkedin = "linkedin"
    x = "x"
    youtube = "youtube"
    blog = "blog"
    website = "website"
    other = "other"


class Tone(str, Enum):
    """Preferred brand voice tone."""

    professional = "professional"
    friendly = "friendly"
    playful = "playful"
    bold = "bold"
    luxurious = "luxurious"
    minimalist = "minimalist"
    other = "other"


class LengthPreference(str, Enum):
    """Preferred output length."""

    short = "short"
    medium = "medium"
    long = "long"


class BrandVoice(BaseModel):
    """Brand voice settings used to shape the prompt."""

    tone: Tone = Field(default=Tone.professional, description="Overall tone of voice.")
    keywords: List[str] = Field(
        default_factory=list,
        description="Key words/phrases to include or emphasize.",
        max_length=30,
    )
    avoid: List[str] = Field(
        default_factory=list,
        description="Words/phrases to avoid using.",
        max_length=30,
    )


class BrandSettings(BaseModel):
    """Brand configuration used for prompt generation."""

    brand_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Brand name to reference in the generated content.",
        examples=["Acme Coffee Co."],
    )
    tagline: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional brand tagline.",
        examples=["Fuel your day, one cup at a time."],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=800,
        description="Optional brand description, values, or positioning.",
    )
    target_audience: Optional[str] = Field(
        default=None,
        max_length=400,
        description="Who the message should be tailored for.",
    )
    voice: BrandVoice = Field(
        default_factory=BrandVoice, description="Preferred voice characteristics."
    )


class StyleSettings(BaseModel):
    """Stylistic preferences for the generated output."""

    length: LengthPreference = Field(
        default=LengthPreference.medium, description="Desired length of the output."
    )
    include_hashtags: bool = Field(
        default=True,
        description="If true, instruct the output to include hashtags when relevant.",
    )
    emoji_level: int = Field(
        default=0,
        ge=0,
        le=5,
        description="How many emojis to include (0 = none, 5 = heavy).",
    )
    formatting_notes: Optional[str] = Field(
        default=None,
        max_length=400,
        description="Extra formatting constraints (e.g., 'use bullet points').",
    )


class PromptGenerateRequest(BaseModel):
    """Request body for generating a prompt."""

    orientation: Orientation = Field(..., description="Content intent / type.")
    platform: Platform = Field(..., description="Target publishing platform.")
    brief: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's content brief / idea / topic / offer to promote.",
    )
    brand: BrandSettings = Field(..., description="Brand configuration.")
    style: StyleSettings = Field(default_factory=StyleSettings, description="Style prefs.")
    additional_context: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional extra context (campaign, constraints, references).",
    )


class PromptGenerateResponse(BaseModel):
    """Response containing the constructed prompt and some helpful metadata."""

    prompt: str = Field(..., description="Constructed prompt text to be sent to an LLM.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional info used to build the prompt (for debugging/UX).",
    )


class Option(BaseModel):
    """Generic key/label option for UI dropdowns."""

    key: str = Field(..., description="Stable identifier (machine-readable).")
    label: str = Field(..., description="Human-friendly label.")


class PublicConfigResponse(BaseModel):
    """Public configuration values and supported options for the frontend."""

    orientations: List[Option] = Field(..., description="Supported orientations.")
    platforms: List[Option] = Field(..., description="Supported platforms.")
    tones: List[Option] = Field(..., description="Supported tones.")
    length_preferences: List[Option] = Field(..., description="Supported length options.")
    version: str = Field(..., description="Backend version string.")
    docs_url: Optional[HttpUrl] = Field(
        default=None, description="Optional docs URL for this backend."
    )


class DefaultSettingsResponse(BaseModel):
    """Reasonable defaults the frontend can use to initialize settings."""

    brand: BrandSettings = Field(..., description="Default brand settings.")
    style: StyleSettings = Field(..., description="Default style settings.")
