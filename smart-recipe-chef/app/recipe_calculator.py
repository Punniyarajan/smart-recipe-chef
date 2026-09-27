import re
from fractions import Fraction
from typing import Any, Dict, List

def scale_ingredient_quantity(ingredient: str, scale_factor: float) -> str:
    """Scales numeric quantities (integers, floats, fractions) in an ingredient string.

    Args:
        ingredient: Ingredient string (e.g. '1/2 cup Olive Oil', '400g Pasta', '3 cloves Garlic').
        scale_factor: Multiplier to scale quantities.

    Returns:
        Scaled ingredient string.
    """
    def replacer(match):
        num_str = match.group(0)
        try:
            if "/" in num_str:
                val = float(Fraction(num_str))
            else:
                val = float(num_str)
            scaled = val * scale_factor
            if scaled == int(scaled):
                return str(int(scaled))
            elif round(scaled, 1) == round(scaled, 2):
                return f"{round(scaled, 1):g}"
            else:
                return f"{round(scaled, 2):g}"
        except Exception:
            return num_str

    pattern = r"\b(?:\d+\/\d+|\d+\.\d+|\d+)\b"
    return re.sub(pattern, replacer, ingredient, count=1)

def estimate_nutrition(ingredients: List[str], target_servings: int) -> Dict[str, Dict[str, float]]:
    """Estimates macro nutritional breakdown (calories, protein, carbs, fat) per serving and total.

    Args:
        ingredients: List of ingredient strings.
        target_servings: Target serving count.

    Returns:
        Dict with 'per_serving' and 'total' macro breakdowns.
    """
    base_calories_per_serving = 480.0
    base_protein_g = 18.0
    base_carbs_g = 55.0
    base_fat_g = 16.0

    text = " ".join(ingredients).lower()

    if any(k in text for k in ["oil", "cheese", "nuts", "butter", "tahini", "avocado", "parmesan"]):
        base_fat_g += 8.0
        base_calories_per_serving += 70.0
    if any(k in text for k in ["chicken", "tofu", "beans", "chickpeas", "fish", "meat", "egg", "protein", "parmesan"]):
        base_protein_g += 10.0
        base_calories_per_serving += 50.0
    if any(k in text for k in ["pasta", "rice", "quinoa", "tortillas", "bread", "potato", "spaghetti", "penne"]):
        base_carbs_g += 15.0
        base_calories_per_serving += 60.0

    per_serving = {
        "calories_kcal": round(base_calories_per_serving, 1),
        "protein_g": round(base_protein_g, 1),
        "carbs_g": round(base_carbs_g, 1),
        "fat_g": round(base_fat_g, 1),
    }

    total = {
        "calories_kcal": round(base_calories_per_serving * target_servings, 1),
        "protein_g": round(base_protein_g * target_servings, 1),
        "carbs_g": round(base_carbs_g * target_servings, 1),
        "fat_g": round(base_fat_g * target_servings, 1),
    }

    return {
        "per_serving": per_serving,
        "total": total
    }

def scale_recipe_and_calculate_macros(
    recipe_title: str,
    original_servings: int,
    target_servings: int,
    ingredients: List[str],
) -> Dict[str, Any]:
    """Scales ingredient quantities for a recipe to a target serving size and calculates estimated macro-nutritional information.

    Args:
        recipe_title: Name of the dish or recipe.
        original_servings: Original number of servings (e.g. 2).
        target_servings: Desired target number of servings (e.g. 6).
        ingredients: List of ingredient strings with quantities (e.g. ['400g Pasta', '2 cups Fresh Basil', '1/2 cup Olive Oil']).

    Returns:
        A dictionary containing scaled ingredients, scaling factor, and macro-nutritional breakdowns per serving and in total.
    """
    if original_servings < 1:
        original_servings = 1
    if target_servings < 1:
        target_servings = 1

    scale_factor = target_servings / original_servings

    scaled_ingredients = [
        scale_ingredient_quantity(ing, scale_factor) for ing in ingredients
    ]

    nutrition = estimate_nutrition(ingredients, target_servings)

    return {
        "recipe_title": recipe_title,
        "original_servings": original_servings,
        "target_servings": target_servings,
        "scale_factor": round(scale_factor, 2),
        "scaled_ingredients": scaled_ingredients,
        "nutrition_per_serving": nutrition["per_serving"],
        "total_nutrition": nutrition["total"],
    }
