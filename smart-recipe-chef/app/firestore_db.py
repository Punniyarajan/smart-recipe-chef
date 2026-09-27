import json
from typing import Any, Dict, List, Optional
import google.auth
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-2faa1f546ea7"
COLLECTION_NAME = "recipes"

_db_client: Optional[firestore.Client] = None

def get_firestore_client() -> firestore.Client:
    global _db_client
    if _db_client is None:
        try:
            creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            _db_client = firestore.Client(project=PROJECT_ID, credentials=creds)
        except Exception:
            _db_client = firestore.Client(project=PROJECT_ID)
    return _db_client

def list_recipes(cuisine: Optional[str] = None, dietary_tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """List or search recipes from the Firestore database.

    Args:
        cuisine: Optional cuisine filter (e.g. "Italian", "Mexican", "Mediterranean").
        dietary_tag: Optional dietary tag filter (e.g. "vegetarian", "vegan", "gluten-free", "quick").

    Returns:
        A list of matching recipe dictionaries.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)

    if cuisine:
        query = query.where("cuisine", "==", cuisine)

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if dietary_tag:
            tags = [t.lower() for t in data.get("dietary_tags", [])]
            if dietary_tag.lower() not in tags:
                continue
        results.append(data)
    return results

def get_recipe(recipe_id: str) -> Dict[str, Any]:
    """Retrieve details for a specific recipe by its ID.

    Args:
        recipe_id: The unique identifier of the recipe (e.g., 'classic-pesto-pasta').

    Returns:
        The recipe dictionary or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(recipe_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    else:
        return {"error": f"Recipe with ID '{recipe_id}' not found."}

def add_recipe(
    recipe_id: str,
    title: str,
    description: str,
    cuisine: str,
    prep_time_mins: int,
    cook_time_mins: int,
    servings: int,
    ingredients: List[str],
    instructions: List[str],
    dietary_tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a new recipe or save a generated recipe to the Firestore database.

    Args:
        recipe_id: A URL-friendly slug ID (e.g., 'mediterranean-quinoa-bowl').
        title: Recipe title.
        description: Brief description of the dish.
        cuisine: Cuisine category (e.g. 'Mediterranean', 'Mexican', 'Italian').
        prep_time_mins: Preparation time in minutes.
        cook_time_mins: Cooking time in minutes.
        servings: Number of servings.
        ingredients: List of ingredient strings with quantities.
        instructions: Step-by-step cooking instructions.
        dietary_tags: List of dietary tags (e.g., ['vegan', 'gluten-free']).

    Returns:
        Status message with saved recipe details.
    """
    db = get_firestore_client()
    data = {
        "title": title,
        "description": description,
        "cuisine": cuisine,
        "prep_time_mins": prep_time_mins,
        "cook_time_mins": cook_time_mins,
        "servings": servings,
        "ingredients": ingredients,
        "instructions": instructions,
        "dietary_tags": dietary_tags or [],
    }
    db.collection(COLLECTION_NAME).document(recipe_id).set(data)
    data["id"] = recipe_id
    return {"status": "success", "message": f"Recipe '{title}' saved successfully.", "recipe": data}
