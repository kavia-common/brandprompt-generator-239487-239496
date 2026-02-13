import pytest

from src.api.models import (
    BrandSettings,
    BrandVoice,
    LengthPreference,
    Orientation,
    Platform,
    PromptGenerateRequest,
    StyleSettings,
    Tone,
)
from src.api.prompt_builder import build_prompt


def _make_request(
    *,
    orientation: Orientation = Orientation.post,
    platform: Platform = Platform.linkedin,
    brand_name: str = "Acme Coffee Co.",
    brief: str = "Launch a new seasonal latte.",
    include_hashtags: bool = True,
    emoji_level: int = 0,
) -> PromptGenerateRequest:
    """Test helper to create a valid PromptGenerateRequest."""
    return PromptGenerateRequest(
        orientation=orientation,
        platform=platform,
        brief=brief,
        additional_context="Promo runs next week.",
        brand=BrandSettings(
            brand_name=brand_name,
            tagline="Fuel your day, one cup at a time.",
            description="Small-batch coffee roaster.",
            target_audience="Busy professionals",
            voice=BrandVoice(tone=Tone.professional, keywords=["seasonal", "craft"], avoid=["cheap"]),
        ),
        style=StyleSettings(
            length=LengthPreference.medium,
            include_hashtags=include_hashtags,
            emoji_level=emoji_level,
            formatting_notes="Use bullet points when listing benefits.",
        ),
    )


def test_build_prompt_includes_major_sections_and_metadata_values():
    req = _make_request(orientation=Orientation.ad, platform=Platform.instagram, brand_name="Acme")

    prompt, metadata = build_prompt(req)

    # Prompt structure
    assert "## Task" in prompt
    assert "## Brand" in prompt
    assert "## Voice & Constraints" in prompt
    assert "## Style" in prompt
    assert "## User Brief" in prompt
    assert "## Additional Context" in prompt
    assert "## Output Requirements" in prompt

    # Key content inclusions
    assert "Create ad-focused copy" in prompt
    assert "Optimize for Instagram" in prompt
    assert "Brand name: Acme" in prompt
    assert "Tone: professional" in prompt
    assert "Include/Emphasize keywords: seasonal, craft" in prompt
    assert "Avoid: cheap" in prompt
    assert "Formatting notes: Use bullet points when listing benefits." in prompt
    assert "Launch a new seasonal latte." in prompt
    assert "Promo runs next week." in prompt

    # Metadata matches normalized values
    assert metadata["orientation"] == "ad"
    assert metadata["platform"] == "instagram"
    assert metadata["brand_name"] == "Acme"
    assert metadata["tone"] == "professional"
    assert metadata["length"] == "medium"
    assert metadata["include_hashtags"] is True
    assert metadata["emoji_level"] == 0


@pytest.mark.parametrize(
    "include_hashtags,expected",
    [
        (True, "Include relevant hashtags at the end."),
        (False, "Do not include hashtags."),
    ],
)
def test_build_prompt_hashtag_instruction(include_hashtags, expected):
    req = _make_request(include_hashtags=include_hashtags)
    prompt, _ = build_prompt(req)
    assert expected in prompt


def test_build_prompt_emoji_instruction_level_zero_and_nonzero():
    req0 = _make_request(emoji_level=0)
    prompt0, _ = build_prompt(req0)
    assert "Do not use emojis." in prompt0

    req3 = _make_request(emoji_level=3)
    prompt3, _ = build_prompt(req3)
    assert "Use emojis sparingly at level 3/5." in prompt3
