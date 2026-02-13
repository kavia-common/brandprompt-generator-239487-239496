from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as prompt_extension_router

openapi_tags = [
    {
        "name": "Prompt Extension",
        "description": "Endpoints used by the browser extension to fetch config/defaults and generate prompts.",
    },
    {"name": "Health", "description": "Service health checks."},
]

app = FastAPI(
    title="Prompt Extension Backend",
    description=(
        "Backend for the browser extension that constructs on-brand prompts from "
        "orientation/platform/brand/style inputs."
    ),
    version="0.2.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prompt_extension_router)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Simple health check endpoint.",
    operation_id="health_check",
)
def health_check():
    """Health check endpoint.

    Returns:
        dict: A small JSON payload confirming the service is running.
    """
    return {"message": "Healthy"}
