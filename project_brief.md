# My agent: Smart Recipe Chef

One-liner: A conversational agent that helps home cooks plan meals, track pantry inventory, and create custom recipes tailored to their dietary preferences and available ingredients.

Tool coverage:
- Memory: Remembers user dietary restrictions (e.g., vegan, gluten-free, allergies), favorite cuisines, household size, and cooking skill level across sessions.
- Tools: Looks up available ingredients in pantry, searches recipe database, updates ingredient stock, and generates meal plans.
- Catalog/UI: Collection of recipes rendered as interactive A2UI cards (showing ingredients, prep time, difficulty, and steps).
- Image gen: Generates appetizing AI presentation photos of recommended or newly created dishes.
- Sandbox: Calculates scaled ingredient quantities based on portion/serving size adjustments and computes macro-nutritional breakdowns.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for recipe scaling/nutrition calculations, Cloud Storage for saving user custom recipe photos, Cloud Trace for observability.
