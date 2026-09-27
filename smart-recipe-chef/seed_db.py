"""Seed script to populate initial recipe items into Firestore."""
import google.auth
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-2faa1f546ea7"
COLLECTION_NAME = "recipes"

SEED_RECIPES = [
    {
        "id": "classic-pesto-pasta",
        "title": "Classic Pesto Pasta",
        "description": "A fragrant, quick Italian pasta dish with homemade basil pesto and toasted pine nuts.",
        "cuisine": "Italian",
        "prep_time_mins": 15,
        "cook_time_mins": 10,
        "servings": 4,
        "ingredients": [
            "400g Penne or Spaghetti",
            "2 cups Fresh Basil leaves",
            "1/2 cup Grated Parmesan cheese",
            "1/3 cup Toasted Pine Nuts",
            "3 cloves Garlic",
            "1/2 cup Extra Virgin Olive Oil",
            "Salt & Black Pepper to taste"
        ],
        "instructions": [
            "Boil pasta in salted water until al dente.",
            "Blend basil, garlic, pine nuts, and parmesan in a food processor.",
            "Slowly drizzle in olive oil while blending until smooth pesto forms.",
            "Toss cooked pasta with pesto sauce and serve warm."
        ],
        "dietary_tags": ["vegetarian", "quick"]
    },
    {
        "id": "mediterranean-quinoa-bowl",
        "title": "Mediterranean Quinoa Bowl",
        "description": "A fresh, protein-packed bowl loaded with cucumbers, cherry tomatoes, olives, and lemon-tahini dressing.",
        "cuisine": "Mediterranean",
        "prep_time_mins": 15,
        "cook_time_mins": 15,
        "servings": 2,
        "ingredients": [
            "1 cup Fluffy Cooked Quinoa",
            "1 cup Cherry Tomatoes (halved)",
            "1 cup Diced Cucumber",
            "1/2 cup Kalamata Olives",
            "1/2 cup Chickpeas (rinsed)",
            "2 tbsp Tahini",
            "1 tbsp Fresh Lemon Juice",
            "1 tbsp Olive Oil"
        ],
        "instructions": [
            "Cook quinoa according to package directions and let cool slightly.",
            "Arrange quinoa, tomatoes, cucumbers, olives, and chickpeas in bowls.",
            "Whisk tahini, lemon juice, olive oil, and 1 tbsp warm water for dressing.",
            "Drizzle dressing over bowls and enjoy."
        ],
        "dietary_tags": ["vegan", "gluten-free", "healthy"]
    },
    {
        "id": "smokey-black-bean-tacos",
        "title": "Smokey Black Bean Tacos",
        "description": "Flavorful, spiced black bean tacos served with fresh avocado salsa and lime juice.",
        "cuisine": "Mexican",
        "prep_time_mins": 10,
        "cook_time_mins": 10,
        "servings": 3,
        "ingredients": [
            "1 can (15oz) Black Beans (drained)",
            "1 tsp Cumin",
            "1/2 tsp Smoked Paprika",
            "6 Small Corn Tortillas",
            "1 Ripe Avocado (diced)",
            "1/2 cup Chopped Fresh Cilantro",
            "1 Lime (cut into wedges)"
        ],
        "instructions": [
            "Warm black beans in a skillet with cumin, smoked paprika, and salt.",
            "Warm corn tortillas on a dry skillet or open flame.",
            "Fill tortillas with black beans and top with avocado and cilantro.",
            "Squeeze fresh lime juice before serving."
        ],
        "dietary_tags": ["vegan", "gluten-free", "quick"]
    }
]

def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        db = firestore.Client(project=PROJECT_ID, credentials=creds)
    except Exception:
        db = firestore.Client(project=PROJECT_ID)

    collection_ref = db.collection(COLLECTION_NAME)

    for item in SEED_RECIPES:
        doc_id = item["id"]
        data = {k: v for k, v in item.items() if k != "id"}
        collection_ref.document(doc_id).set(data)
        print(f"  ✓ Seeded recipe: '{item['title']}' (ID: {doc_id})")

    print(f"Successfully seeded {len(SEED_RECIPES)} recipes into collection '{COLLECTION_NAME}'!")

if __name__ == "__main__":
    seed()
