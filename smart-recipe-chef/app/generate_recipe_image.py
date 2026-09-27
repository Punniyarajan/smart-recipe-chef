from typing import Any, Dict
import google.auth
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-01-2faa1f546ea7"
BUCKET_NAME = "smart-recipe-chef-photos-qwiklabs-gcp-01-2faa1f546ea7"

def generate_recipe_image(
    recipe_title: str,
    tool_context: ToolContext,
    prompt_description: str = "",
) -> Dict[str, Any]:
    """Generates an AI presentation image for a recipe dish using gemini-3.1-flash-lite-image in the global region.

    Saves the image as an artifact in the session context and uploads it to Cloud Storage, returning its public URL.

    Args:
        recipe_title: Name of the dish or recipe (e.g. 'Classic Pesto Pasta').
        tool_context: ADK ToolContext provided automatically by the framework.
        prompt_description: Optional extra visual details for the image generation.

    Returns:
        A dictionary containing the status, recipe title, and public Cloud Storage image URL.
    """
    genai_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    image_prompt = f"A professional, delicious food presentation photograph of {recipe_title}."
    if prompt_description:
        image_prompt += f" {prompt_description}"

    try:
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=image_prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break

        if not image_bytes:
            return {
                "status": "error",
                "message": f"Could not generate image content for '{recipe_title}'.",
            }

        slug = "".join(c for c in recipe_title.lower().replace(" ", "-") if c.isalnum() or c == "-")
        file_ext = "jpg" if "jpeg" in mime_type or "jpg" in mime_type else "png"
        filename = f"{slug or 'recipe-photo'}.{file_ext}"

        # 1. Save as artifact in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload same image bytes to public Cloud Storage bucket
        try:
            creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            storage_client = storage.Client(project=PROJECT_ID, credentials=creds)
        except Exception:
            storage_client = storage.Client(project=PROJECT_ID)

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "recipe_title": recipe_title,
            "image_url": public_url,
            "message": f"Successfully generated photo for '{recipe_title}', recorded artifact, and published to Cloud Storage.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Image generation failed: {str(e)}"}
