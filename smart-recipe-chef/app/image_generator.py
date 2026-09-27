from typing import Any, Dict
import google.auth
from google.cloud import storage

PROJECT_ID = "qwiklabs-gcp-01-2faa1f546ea7"
BUCKET_NAME = "smart-recipe-chef-photos-qwiklabs-gcp-01-2faa1f546ea7"

def generate_dish_photo(recipe_title: str, description: str = "") -> Dict[str, Any]:
    """Generates an appetizing dish photo presentation card and uploads it to Cloud Storage.

    Args:
        recipe_title: Title of the dish (e.g., 'Classic Pesto Pasta', 'Smokey Black Bean Tacos').
        description: Short description or tagline of the recipe.

    Returns:
        A dictionary containing the status, recipe title, and public image URL.
    """
    slug = "".join(c for c in recipe_title.lower().replace(" ", "-") if c.isalnum() or c == "-")
    file_name = f"{slug or 'dish'}.svg"

    short_desc = description[:60] if description else "Freshly Prepared Smart Recipe"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1B2E1B"/>
      <stop offset="100%" stop-color="#0E190E"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4CAF50"/>
      <stop offset="100%" stop-color="#8BC34A"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" rx="16" fill="url(#bg)"/>
  <circle cx="300" cy="170" r="110" fill="#2E4A2E" opacity="0.6"/>
  <circle cx="300" cy="170" r="95" fill="#3B5E3B" opacity="0.8"/>
  <text x="300" y="182" font-family="Arial, sans-serif" font-size="70" text-anchor="middle">🍽️</text>
  <rect x="40" y="290" width="520" height="4" rx="2" fill="url(#accent)"/>
  <text x="300" y="325" font-family="Georgia, serif" font-size="24" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{recipe_title}</text>
  <text x="300" y="355" font-family="Arial, sans-serif" font-size="14" fill="#A0C8A0" text-anchor="middle">{short_desc}</text>
</svg>"""

    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        client = storage.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        client = storage.Client(project=PROJECT_ID)

    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    blob.upload_from_string(svg_content, content_type="image/svg+xml")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{file_name}"
    return {
        "status": "success",
        "recipe_title": recipe_title,
        "image_url": public_url,
        "message": f"Dish photo for '{recipe_title}' saved to Cloud Storage."
    }
