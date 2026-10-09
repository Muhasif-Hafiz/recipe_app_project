# Recipe Studio

A beginner-friendly recipe app built with Streamlit and Google's Gemini API.

## 1. Open the project in VS Code

Unzip the project, then open the `recipe_app_project` folder in VS Code.

## 2. Create a virtual environment (Mac)

Open **Terminal** in VS Code and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Configure your Gemini API key

Copy `.env.example` to a new file named `.env` in the same folder as `app.py`.
Open `.env` and replace `put_your_gemini_api_key_here` with your own key.

Do not put quotation marks around the key, and never paste it into chat or commit `.env` to Git.

## 4. Run the app

In the same VS Code terminal, run:

```bash
streamlit run app.py
```

Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Features

- Ingredients-based recipe generation
- Cuisine and dietary preferences
- Servings, time limit, and skill level
- Recipe ingredients and numbered instructions
- Tips, substitutions, storage advice, and approximate nutrition
- Download recipe as JSON
- API key loaded from `.env` rather than hard-coded in source

## Troubleshooting

- If `streamlit` is not found, make sure `.venv` is activated and dependencies installed. You can also run `python -m streamlit run app.py`.
- If the app says `GEMINI_API_KEY is missing`, check that `.env` is in the same folder as `app.py` and contains `GEMINI_API_KEY=...`.
- If a model is unavailable, set `GEMINI_MODEL` in `.env` to a model name enabled for your API account.
