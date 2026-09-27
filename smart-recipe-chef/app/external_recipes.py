import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict

def search_external_recipes(query: str) -> Dict[str, Any]:
    """Search for global recipe ideas and instructions from TheMealDB public food database.

    Args:
        query: Ingredient or dish name to search for (e.g. 'pasta', 'chicken', 'tacos', 'salad').

    Returns:
        A dictionary containing a list of matching meals with ingredients, category, and instructions.
    """
    api_key = os.getenv("MEALDB_API_KEY", "1")
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={urllib.parse.quote(query)}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SmartRecipeChef/1.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            meals = data.get("meals")
            if not meals:
                return {
                    "status": "success",
                    "query": query,
                    "count": 0,
                    "results": [],
                    "message": f"No external recipes found for '{query}'."
                }

            results = []
            for meal in meals[:3]:
                ingredients = []
                for i in range(1, 21):
                    ing = meal.get(f"strIngredient{i}")
                    measure = meal.get(f"strMeasure{i}")
                    if ing and ing.strip():
                        ingredients.append(f"{measure.strip() if measure else ''} {ing.strip()}".strip())

                instructions = meal.get("strInstructions", "")
                if len(instructions) > 300:
                    instructions = instructions[:300] + "..."

                results.append({
                    "meal_id": meal.get("idMeal"),
                    "title": meal.get("strMeal"),
                    "category": meal.get("strCategory"),
                    "area": meal.get("strArea"),
                    "instructions": instructions,
                    "ingredients": ingredients,
                    "thumbnail_url": meal.get("strMealThumb"),
                })

            return {
                "status": "success",
                "query": query,
                "count": len(results),
                "results": results,
            }
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch external recipes: {str(e)}"}
