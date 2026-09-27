import base64
from typing import Any, Dict
import google.auth
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-01-2faa1f546ea7"
BUCKET_NAME = "smart-recipe-chef-photos-qwiklabs-gcp-01-2faa1f546ea7"

def generate_recipe_video(
    recipe_title: str,
    tool_context: ToolContext,
    prompt_description: str = "",
) -> Dict[str, Any]:
    """Generates a short culinary demonstration video for a recipe dish using gemini-omni-flash-preview in the global region.

    Saves the video as an artifact in the session context and uploads it to Cloud Storage, returning its public URL.

    Args:
        recipe_title: Name of the dish or recipe (e.g. 'Spaghetti Carbonara').
        tool_context: ADK ToolContext provided automatically by the framework.
        prompt_description: Optional visual details for the video generation.

    Returns:
        A dictionary containing the status, recipe title, and public Cloud Storage video URL.
    """
    genai_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    video_prompt = f"A short 5-second culinary video demonstrating how to prepare or serve {recipe_title}."
    if prompt_description:
        video_prompt += f" {prompt_description}"

    try:
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=video_prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        if interaction and hasattr(interaction, "output_video") and interaction.output_video:
            vid = interaction.output_video
            if hasattr(vid, "mime_type") and vid.mime_type:
                mime_type = vid.mime_type
            if hasattr(vid, "data") and vid.data:
                if isinstance(vid.data, str):
                    video_bytes = base64.b64decode(vid.data)
                elif isinstance(vid.data, bytes):
                    video_bytes = vid.data

        if not video_bytes:
            return {
                "status": "error",
                "message": f"Could not generate video content for '{recipe_title}'.",
            }

        slug = "".join(c for c in recipe_title.lower().replace(" ", "-") if c.isalnum() or c == "-")
        filename = f"{slug or 'recipe-video'}.mp4"

        # 1. Save as artifact in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload same video bytes directly to public Cloud Storage bucket
        try:
            creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            storage_client = storage.Client(project=PROJECT_ID, credentials=creds)
        except Exception:
            storage_client = storage.Client(project=PROJECT_ID)

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return {
            "status": "success",
            "recipe_title": recipe_title,
            "video_url": public_url,
            "message": f"Successfully generated video for '{recipe_title}', recorded artifact, and published to Cloud Storage.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Video generation failed: {str(e)}"}
