import os
import json
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from a local .env file.
load_dotenv()

APP_TITLE = "Recipe Studio"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def get_gemini_client() -> genai.Client:
    """Create a Gemini client using GEMINI_API_KEY from the environment."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file, then restart the app."
        )
    return genai.Client(api_key=api_key)


def generate_recipe(
    ingredients: list[str],
    cuisine: str,
    diet: str,
    servings: int,
    max_minutes: int,
    skill_level: str,
    extra_requests: str = "",
) -> dict[str, Any]:
    """Ask Gemini to generate a structured recipe and return it as a dictionary."""
    client = get_gemini_client()

    prompt = f"""
You are a careful, creative recipe developer. Create one practical recipe based on
the user's available ingredients and preferences.

Available ingredients: {", ".join(ingredients)}
Cuisine: {cuisine}
Dietary preference: {diet}
Servings: {servings}
Maximum total time: {max_minutes} minutes
Cooking experience: {skill_level}
Additional requests: {extra_requests or "None"}

Important requirements:
- Respect the dietary preference. For Jain recipes, avoid onion, garlic, and root vegetables
  unless the user explicitly says otherwise. If unsure about a restriction, mention it.
- Use the listed ingredients where practical and clearly list any additional pantry items.
- Do not claim the recipe is allergy-safe. Mention that packaged ingredients and cross-contact
  should be checked for allergies.
- Give realistic quantities, clear numbered steps, preparation and cooking time, and servings.
- Include substitutions, storage guidance, and approximate nutrition per serving when possible.
- Be concise but complete.
- Return valid JSON only, with this exact structure:
{{
  "title": "Recipe title",
  "description": "Short appetizing description",
  "prep_time_minutes": 10,
  "cook_time_minutes": 20,
  "servings": {servings},
  "difficulty": "Easy",
  "ingredients": [
    {{"item": "ingredient name", "quantity": "quantity", "note": "optional note"}}
  ],
  "instructions": ["Step 1", "Step 2"],
  "tips": ["Helpful tip"],
  "substitutions": ["Possible substitution"],
  "storage": "Storage advice",
  "nutrition_per_serving": {{
    "calories": "approximate value or unavailable",
    "protein": "approximate value or unavailable",
    "carbohydrates": "approximate value or unavailable",
    "fat": "approximate value or unavailable"
  }},
  "dietary_notes": ["Relevant dietary note"]
}}
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    try:
        recipe = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned a response that could not be read. Please try again."
        ) from exc

    if not isinstance(recipe, dict) or not recipe.get("title"):
        raise RuntimeError("The generated recipe was incomplete. Please try again.")
    return recipe


def render_recipe(recipe: dict[str, Any]) -> None:
    """Render a recipe in a readable Streamlit layout."""
    st.markdown(f"# {recipe.get('title', 'Your Recipe')}")
    st.write(recipe.get("description", ""))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Prep time", f"{recipe.get('prep_time_minutes', '—')} min")
    c2.metric("Cook time", f"{recipe.get('cook_time_minutes', '—')} min")
    c3.metric("Servings", str(recipe.get("servings", "—")))
    c4.metric("Difficulty", str(recipe.get("difficulty", "—")))

    st.subheader("Ingredients")
    ingredients = recipe.get("ingredients", [])
    if ingredients:
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                item = ingredient.get("item", "Ingredient")
                quantity = ingredient.get("quantity", "")
                note = ingredient.get("note", "")
                line = f"- **{quantity}** {item}".strip()
                if note:
                    line += f" — {note}"
                st.markdown(line)
            else:
                st.markdown(f"- {ingredient}")

    st.subheader("Instructions")
    for index, instruction in enumerate(recipe.get("instructions", []), start=1):
        st.markdown(f"{index}. {instruction}")

    tips = recipe.get("tips", [])
    if tips:
        with st.expander("Cooking tips"):
            for tip in tips:
                st.markdown(f"- {tip}")

    substitutions = recipe.get("substitutions", [])
    if substitutions:
        with st.expander("Ingredient substitutions"):
            for item in substitutions:
                st.markdown(f"- {item}")

    if recipe.get("storage"):
        with st.expander("Storage advice"):
            st.write(recipe["storage"])

    nutrition = recipe.get("nutrition_per_serving", {})
    if nutrition:
        with st.expander("Approximate nutrition per serving"):
            for key, value in nutrition.items():
                st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
            st.caption("Nutrition values are estimates, not medical or dietary advice.")

    dietary_notes = recipe.get("dietary_notes", [])
    if dietary_notes:
        with st.expander("Dietary notes"):
            for note in dietary_notes:
                st.markdown(f"- {note}")

    st.caption(
        "Check ingredient labels and avoid cross-contact if you have food allergies. "
        "AI-generated recipes and nutrition estimates can be imperfect."
    )

    st.download_button(
        "Download recipe as JSON",
        data=json.dumps(recipe, indent=2, ensure_ascii=False),
        file_name="recipe.json",
        mime="application/json",
        use_container_width=True,
    )


st.set_page_config(page_title=APP_TITLE, page_icon="🍲", layout="wide")

st.title("🍲 Recipe Studio")
st.write("Turn the ingredients you have into a recipe tailored to your taste.")

with st.sidebar:
    st.header("Your preferences")
    cuisine = st.selectbox(
        "Cuisine",
        ["Any", "Indian", "Italian", "Mexican", "Chinese", "Mediterranean", "Thai", "Other"],
    )
    diet = st.selectbox(
        "Dietary preference",
        ["No specific preference", "Vegetarian", "Vegan", "Jain", "Pescatarian", "Gluten-free", "Dairy-free"],
    )
    servings = st.slider("Servings", min_value=1, max_value=12, value=2)
    max_minutes = st.slider("Maximum total time (minutes)", 10, 180, 40, step=5)
    skill_level = st.selectbox("Cooking experience", ["Beginner", "Intermediate", "Confident"])
    st.caption(f"Model: `{DEFAULT_MODEL}`")

with st.form("recipe_form"):
    ingredient_text = st.text_area(
        "What ingredients do you have?",
        placeholder="e.g. tomatoes, lentils, onion, cumin, rice, spinach",
        help="Separate ingredients with commas or put each on a new line.",
        height=110,
    )
    extra_requests = st.text_input(
        "Anything else? (optional)",
        placeholder="e.g. spicy, high-protein, one-pot, no oven",
    )
    submitted = st.form_submit_button("✨ Generate my recipe", type="primary", use_container_width=True)

if submitted:
    ingredients = [
        item.strip()
        for item in ingredient_text.replace("\n", ",").split(",")
        if item.strip()
    ]
    if not ingredients:
        st.warning("Enter at least one ingredient before generating a recipe.")
    else:
        with st.spinner("Creating your recipe…"):
            try:
                recipe = generate_recipe(
                    ingredients=ingredients,
                    cuisine=cuisine,
                    diet=diet,
                    servings=servings,
                    max_minutes=max_minutes,
                    skill_level=skill_level,
                    extra_requests=extra_requests.strip(),
                )
                st.session_state["last_recipe"] = recipe
                st.success("Your recipe is ready!")
            except Exception as exc:
                st.error(f"Could not generate the recipe: {exc}")
                st.info(
                    "Check that your API key is valid, your internet connection works, "
                    "and the selected Gemini model is available to your account."
                )

if st.session_state.get("last_recipe"):
    st.divider()
    render_recipe(st.session_state["last_recipe"])
else:
    st.info("Add a few ingredients and choose your preferences to get started.")
