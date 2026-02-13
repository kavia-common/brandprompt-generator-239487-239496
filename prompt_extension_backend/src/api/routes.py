"""
API routes for prompt generation and configuration retrieval.
"""

from __future__ import annotations

from fastapi import APIRouter

from src.api.models import (
    DefaultSettingsResponse,
    LengthPreference,
    Option,
    Orientation,
    Platform,
    PromptGenerateRequest,
    PromptGenerateResponse,
    PublicConfigResponse,
    Tone,
)
from src.api.prompt_builder import build_prompt

router = APIRouter(tags=["Prompt Extension"])


@router.get(
    "/config",
    response_model=PublicConfigResponse,
    summary="Get public config/options",
    description="Returns supported enum options and basic backend metadata for the extension UI.",
    operation_id="get_public_config",
)
def get_public_config() -> PublicConfigResponse:
    """Get public configuration and supported options.

    Returns:
        PublicConfigResponse: Supported options used by the frontend to populate dropdowns.
    """
    def _opts(enum_cls):
        return [Option(key=e.value, label=e.value.replace("_", " ").title()) for e in enum_cls]

    return PublicConfigResponse(
        orientations=_opts(Orientation),
        platforms=_opts(Platform),
        tones=_opts(Tone),
        length_preferences=_opts(LengthPreference),
        version="0.2.0",
        docs_url=None,
    )


@router.get(
    "/settings/defaults",
    response_model=DefaultSettingsResponse,
    summary="Get default settings",
    description="Returns default brand/style settings for initializing the extension UI.",
    operation_id="get_default_settings",
)
def get_default_settings() -> DefaultSettingsResponse:
    """Get default settings for the extension UI.

    Returns:
        DefaultSettingsResponse: Default brand/style objects.
    """
    return DefaultSettingsResponse(
        brand={
            "brand_name": "Your Brand",
            "tagline": None,
            "description": None,
            "target_audience": None,
            "voice": {"tone": "professional", "keywords": [], "avoid": []},
        },
        style={
            "length": "medium",
            "include_hashtags": True,
            "emoji_level": 0,
            "formatting_notes": None,
        },
    )


@router.post(
    "/prompts/generate",
    response_model=PromptGenerateResponse,
    summary="Generate a prompt",
    description=(
        "Builds a structured prompt from orientation/platform/brand/style inputs. "
        "This endpoint does not call any external LLM; it returns the prompt for the client to use."
    ),
    operation_id="generate_prompt",
)
def generate_prompt(body: PromptGenerateRequest) -> PromptGenerateResponse:
    """Generate a prompt for the user based on selected settings.

    Args:
        body: Validated prompt generation request.

    Returns:
        PromptGenerateResponse: The constructed prompt and metadata.
    """
    prompt, metadata = build_prompt(body)
    return PromptGenerateResponse(prompt=prompt, metadata=metadata)
