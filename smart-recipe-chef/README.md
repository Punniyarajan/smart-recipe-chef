# Smart Recipe Chef 🍳

An intelligent, multi-tool culinary AI assistant powered by Google Agent Development Kit (ADK), Vertex AI Agent Engine, and Generative UI (A2UI).

![Smart Recipe Chef Demo](./demo.gif)

---

## 🌟 Capabilities & Features

Smart Recipe Chef combines LLM reasoning with Google Cloud services to deliver an end-to-end culinary workspace:

- **Recipe Box Management (Cloud Firestore)**: Save, retrieve, and list personal recipes in a structured Firestore database (`add_recipe`, `get_recipe`, `list_recipes`).
- **Ingredient Scaling & Macro Calculation**: Dynamically scale ingredient quantities for any serving size and compute total calories, protein, carbs, and fat breakdowns (`scale_recipe_and_calculate_macros`).
- **Global Recipe Search**: Query external culinary databases via TheMealDB API to discover dishes from around the world (`search_external_recipes`).
- **AI Dish Photo Generation**: Generate high-resolution food presentation photos using Vertex AI `gemini-3.1-flash-lite-image` in the `global` region (`generate_recipe_image`). Automatically records session artifacts and publishes to a public Google Cloud Storage bucket.
- **AI Cooking Video Generation**: Generate short video demonstrations of dish preparation using Vertex AI `gemini-omni-flash-preview` in the `global` region (`generate_recipe_video`). Automatically records session artifacts and publishes directly to Cloud Storage.
- **Nearby Grocery Store Finder**: Geocode addresses and locate nearby grocery stores or food markets using the Google Maps Places API (`geocode_address`, `find_nearby_places`).
- **Cross-Session Memory & Allergy Tracking**: Uses Vertex AI Memory Bank (`VertexAiMemoryBankService`, `PreloadMemoryTool`) to remember user dietary restrictions, food allergies, and preferences across sessions.
- **Generative UI (A2UI)**: Transforms structured tool outputs into rich, interactive card surfaces rendered over the A2A protocol.
- **Sandbox Code Execution**: Safely evaluates custom Python code in an isolated Vertex AI Agent Engine sandbox environment (`AgentEngineSandboxCodeExecutor`).

---

## ☁️ Google Cloud & API Architecture

Smart Recipe Chef integrates with the following Google Cloud services and APIs:

| Component / Service | Implementation / Model | Description |
| :--- | :--- | :--- |
| **Agent Framework** | Google ADK (`google-adk`) | Root agent orchestration and tool execution |
| **Primary Model** | `gemini-flash-latest` | Core reasoning and conversation engine |
| **Image Generation** | `gemini-3.1-flash-lite-image` | Generates dish presentation photography |
| **Video Generation** | `gemini-omni-flash-preview` | Generates short cooking demonstration clips |
| **Long-Term Memory** | Vertex AI Memory Bank | Cross-session memory storage for dietary preferences |
| **Database** | Cloud Firestore | Persistent recipe box storage |
| **Media Hosting** | Google Cloud Storage | Public bucket storage for generated images and videos |
| **Location Services** | Google Maps Places API | Geocoding and nearby grocery store discovery |
| **Sandbox Execution** | Vertex AI Agent Engine | Isolated execution sandbox for Python code |
| **UI Framework** | Generative UI (A2UI v0.8) | Dynamic card surface generation |

---

## 📁 Repository Structure

```
smart-recipe-chef/
├── README.md                      # Project documentation
├── demo.gif                       # Automated video walkthrough
├── agents-cli-manifest.yaml       # Agent Engine deployment manifest
├── deployment_metadata.json       # Deployment resource tracking
├── app/                           # Core Agent Application
│   ├── agent.py                   # Root agent definition & tool wiring
│   ├── a2ui_utils.py              # A2UI callback transformer
│   ├── firestore_db.py            # Firestore recipe operations
│   ├── recipe_calculator.py       # Ingredient scaling & macro nutrition
│   ├── external_recipes.py        # TheMealDB external recipe API
│   ├── generate_recipe_image.py   # Imagen 3 photo generation & GCS upload
│   ├── generate_recipe_video.py   # Omni video generation & GCS upload
│   └── maps_tools.py              # Google Maps Places & Geocoding
└── frontend/                      # Web Chat Interface
    ├── main.py                    # FastAPI proxy server
    ├── requirements.txt           # Frontend dependencies
    └── static/
        └── index.html             # Themed culinary chat UI & A2UI renderer
```

---

## 🚀 Local Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Google Cloud Project with Vertex AI, Firestore, and Cloud Storage enabled
- Google Maps API Key

### 1. Clone & Install Dependencies
```bash
git clone <your-repo-url>
cd smart-recipe-chef

# Install agent dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment Variables
Set the environment variables required for the agent and web proxy:

```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
export AGENT_DIRECTORY="app"
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-number>/locations/us-east1/reasoningEngines/<resource-id>"
```

### 3. Run the Frontend Locally
Start the FastAPI server from the `frontend/` directory:

```bash
cd frontend
python main.py
```

The application will initialize on port `8080`.

### 4. Deploying to Vertex AI Agent Engine
To deploy or update the agent on Google Cloud:

```bash
agents-cli deploy \
  --project "<your-gcp-project-id>" \
  --no-confirm-project \
  --update-env-vars "GOOGLE_MAPS_API_KEY=<your-google-maps-api-key>"
```
