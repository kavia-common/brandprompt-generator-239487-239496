from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check_ok():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Healthy"}


def test_get_public_config_contains_expected_options_and_version():
    res = client.get("/config")
    assert res.status_code == 200
    data = res.json()

    assert data["version"] == "0.2.0"
    assert data["docs_url"] is None

    # Ensure we return UI option arrays with key/label
    assert isinstance(data["orientations"], list) and len(data["orientations"]) > 0
    assert isinstance(data["platforms"], list) and len(data["platforms"]) > 0
    assert isinstance(data["tones"], list) and len(data["tones"]) > 0
    assert isinstance(data["length_preferences"], list) and len(data["length_preferences"]) > 0

    first = data["orientations"][0]
    assert "key" in first and "label" in first


def test_get_default_settings_shape_and_defaults():
    res = client.get("/settings/defaults")
    assert res.status_code == 200
    data = res.json()

    assert "brand" in data
    assert "style" in data

    assert data["brand"]["brand_name"] == "Your Brand"
    assert data["brand"]["voice"]["tone"] == "professional"

    assert data["style"]["length"] == "medium"
    assert data["style"]["include_hashtags"] is True
    assert data["style"]["emoji_level"] == 0


def test_generate_prompt_success_includes_prompt_and_metadata():
    payload = {
        "orientation": "post",
        "platform": "linkedin",
        "brief": "Announce our new analytics feature.",
        "additional_context": "Keep it credible and avoid hype.",
        "brand": {
            "brand_name": "Acme Analytics",
            "tagline": "Insights without noise",
            "description": "B2B analytics platform",
            "target_audience": "Data leaders",
            "voice": {"tone": "professional", "keywords": ["credible"], "avoid": ["hype"]},
        },
        "style": {
            "length": "medium",
            "include_hashtags": True,
            "emoji_level": 0,
            "formatting_notes": "Use short paragraphs.",
        },
    }

    res = client.post("/prompts/generate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert isinstance(data["prompt"], str)
    assert len(data["prompt"]) > 50  # should be a structured prompt
    assert "## Task" in data["prompt"]
    assert "Acme Analytics" in data["prompt"]

    # Metadata should be present and aligned
    assert data["metadata"]["orientation"] == "post"
    assert data["metadata"]["platform"] == "linkedin"
    assert data["metadata"]["brand_name"] == "Acme Analytics"
    assert data["metadata"]["tone"] == "professional"
    assert data["metadata"]["length"] == "medium"
    assert data["metadata"]["include_hashtags"] is True
    assert data["metadata"]["emoji_level"] == 0


def test_generate_prompt_validation_error_on_missing_required_fields():
    # Missing required: brand.brand_name, brief, etc.
    bad_payload = {"orientation": "post", "platform": "linkedin", "brand": {}}
    res = client.post("/prompts/generate", json=bad_payload)
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
