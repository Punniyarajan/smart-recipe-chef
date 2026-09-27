# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.external_recipes import search_external_recipes
from app.firestore_db import add_recipe, get_recipe, list_recipes
from app.generate_recipe_image import generate_recipe_image
from app.generate_recipe_video import generate_recipe_video
from app.maps_tools import find_nearby_places, geocode_address
from app.recipe_calculator import scale_recipe_and_calculate_macros

DEPLOYMENT_METADATA_PATH = Path(__file__).parent.parent / "deployment_metadata.json"
PROJECT_ID = "qwiklabs-gcp-01-2faa1f546ea7"
MEMORY_BANK_ID = "6457728658067947520"
LOCATION = "us-east1"

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Smart Recipe Chef, an expert AI culinary assistant. "
        "You help users discover recipes, manage their recipe box in Firestore, "
        "scale ingredient quantities, calculate macro nutrition, generate dish "
        "photos using AI image models saved to Playground artifacts and Cloud "
        "Storage, search global recipes, locate nearby grocery stores using "
        "Google Maps, and safely execute Python code in an Agent Engine sandbox environment."
    ),
    workflow_description=(
        "Analyze the user's culinary request. Use function tools to query Firestore, "
        "search external recipes, scale ingredients, or locate nearby grocery "
        "stores as needed. Whenever returning recipe cards, nutrition breakdowns, "
        "pantry lists, or store locations, present them as clean A2UI surfaces."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects. "
        "CRITICAL ALLERGY & DIETARY MEMORY INSTRUCTIONS: Always check retrieved "
        "user memories for food allergies before suggesting, creating, scaling, "
        "or saving any recipe. Never recommend or generate recipes containing a "
        "known user allergen unless explicit safe substitutes are applied and noted."
    ),
    include_schema=True,
    include_examples=True,
)

async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after each turn to store session memories in Memory Bank."""
    if getattr(callback_context, "memory_service", None) is not None:
        try:
            await callback_context.add_session_to_memory()
        except Exception as e:
            logger.warning(f"Failed to add session to memory: {e}")
    return None

def memory_bank_service_builder():
    """Configures the Vertex AI Memory Bank service for deployed containers."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )

def get_sandbox_code_executor() -> AgentEngineSandboxCodeExecutor:
    """Loads the remote Agent Engine resource ID from deployment_metadata.json and initializes the sandbox code executor."""
    agent_engine_id = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"
    if DEPLOYMENT_METADATA_PATH.exists():
        try:
            with open(DEPLOYMENT_METADATA_PATH) as f:
                data = json.load(f)
                if data.get("remote_agent_runtime_id"):
                    agent_engine_id = data.get("remote_agent_runtime_id")
        except Exception:
            pass

    return AgentEngineSandboxCodeExecutor(agent_engine_resource_name=agent_engine_id)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        list_recipes,
        get_recipe,
        add_recipe,
        scale_recipe_and_calculate_macros,
        generate_recipe_image,
        generate_recipe_video,
        search_external_recipes,
        geocode_address,
        find_nearby_places,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    code_executor=get_sandbox_code_executor(),
)

app = App(
    root_agent=root_agent,
    name="app",
)
