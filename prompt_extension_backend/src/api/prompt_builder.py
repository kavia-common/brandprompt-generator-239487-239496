"""
Prompt construction logic.

This module builds a high-quality, structured prompt string from validated inputs.
The output is intentionally deterministic and does not call any external LLM.
"""

from __future__ import annotations

from typing import Any, Dict

from src.api.models import PromptGenerateRequest


def _join_nonempty(lines: list[str]) -> str:
    return "\n".join([ln for ln in lines if ln and ln.strip()])


def _platform_notes(platform: str) -> str:
    notes = {
        "instagram": "Optimize for Instagram: strong hook, short paragraphs, optional hashtags.",
        "tiktok": "Optimize for TikTok: punchy, conversational, high-energy; include on-screen text suggestions if useful.",
        "facebook": "Optimize for Facebook: clear value proposition, friendly tone, encourage comments/shares when relevant.",
        "linkedin": "Optimize for LinkedIn: professional, credible, insight-driven; avoid slang.",
        "x": "Optimize for X: concise, bold, high signal; consider a short thread if needed.",
        "youtube": "Optimize for YouTube: include a title + hook; structure for spoken delivery if applicable.",
        "blog": "Optimize for blog: outline-first, SEO-aware headings, clear structure.",
        "website": "Optimize for web/landing: benefits-first, scannable sections, clear CTA.",
        "other": "Optimize for the specified platform context.",
    }
    return notes.get(platform, notes["other"])


def _orientation_notes(orientation: str) -> str:
    notes = {
        "post": "Create a social post draft.",
        "ad": "Create ad-focused copy (attention, offer, CTA) and include 2-3 variants.",
        "email": "Create an email draft with subject lines and a clear CTA.",
        "landing_page": "Create landing-page copy with hero, benefits, social proof ideas, and CTA.",
        "other": "Create content appropriate to the intent described.",
    }
    return notes.get(orientation, notes["other"])


# PUBLIC_INTERFACE
def build_prompt(req: PromptGenerateRequest) -> tuple[str, Dict[str, Any]]:
    """Build a structured prompt string and metadata from a validated request.

    Args:
        req: Validated prompt generation request.

    Returns:
        (prompt, metadata) where:
          - prompt is a single string to send to an LLM.
          - metadata includes normalized fields helpful for debugging and UI display.
    """
    brand = req.brand
    style = req.style

    voice_keywords = ", ".join(brand.voice.keywords) if brand.voice.keywords else "N/A"
    avoid_keywords = ", ".join(brand.voice.avoid) if brand.voice.avoid else "N/A"

    length_map = {
        "short": "Keep it concise.",
        "medium": "Keep it moderately detailed.",
        "long": "Make it thorough and detailed.",
    }

    emoji_instruction = (
        "Do not use emojis."
        if style.emoji_level == 0
        else f"Use emojis sparingly at level {style.emoji_level}/5."
    )

    hashtag_instruction = (
        "Include relevant hashtags at the end."
        if style.include_hashtags
        else "Do not include hashtags."
    )

    prompt = _join_nonempty(
        [
            "You are a world-class brand copywriter and prompt engineer.",
            "",
            "## Task",
            _orientation_notes(req.orientation.value),
            _platform_notes(req.platform.value),
            "",
            "## Brand",
            f"Brand name: {brand.brand_name}",
            f"Tagline: {brand.tagline or 'N/A'}",
            f"Description/positioning: {brand.description or 'N/A'}",
            f"Target audience: {brand.target_audience or 'N/A'}",
            "",
            "## Voice & Constraints",
            f"Tone: {brand.voice.tone.value}",
            f"Include/Emphasize keywords: {voice_keywords}",
            f"Avoid: {avoid_keywords}",
            "",
            "## Style",
            f"Length: {style.length.value} ({length_map.get(style.length.value, '')})",
            emoji_instruction,
            hashtag_instruction,
            f"Formatting notes: {style.formatting_notes or 'N/A'}",
            "",
            "## User Brief",
            req.brief.strip(),
            "",
            "## Additional Context",
            (req.additional_context or "N/A").strip(),
            "",
            "## Output Requirements",
            "- Output only the final content (no analysis).",
            "- Ensure the content is on-brand and platform-appropriate.",
            "- Provide 1 primary version, plus variants if the orientation suggests it (e.g., ads).",
        ]
    )

    metadata: Dict[str, Any] = {
        "orientation": req.orientation.value,
        "platform": req.platform.value,
        "brand_name": brand.brand_name,
        "tone": brand.voice.tone.value,
        "length": style.length.value,
        "include_hashtags": style.include_hashtags,
        "emoji_level": style.emoji_level,
    }
    return prompt, metadata
