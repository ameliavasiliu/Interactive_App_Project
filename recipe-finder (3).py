import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd

PRIMARY = "#8fa98c"
DARK = "#4a7a50"
BG = "#b8ccb5"
TEXT = "#1a1a1a"
CREAM = "#f5f1e6"

st.set_page_config(
    page_title="Recipe Finder | Hoos Hungry?",
    layout="centered",
    initial_sidebar_state="expanded"
)

def get_spoonacular_key():
    return st.secrets["api"]["SPOONACULAR_API_KEY"]

def get_gemini_key():
    return st.secrets["api"]["GEMINI_API_KEY"]

with st.sidebar:
    st.header("Advanced Settings")

    max_prep = st.slider("Max Prep Time (minutes)", 5, 120, 60, key="max_prep")
    max_calories = st.slider("Max Calories", 200, 1500, 800, key="max_calories")
    number_results = st.slider("Number of Recipes", 1, 10, 5, key="num_results")

    diet = st.selectbox(
        "Diet Type",
        ["None", "vegetarian", "vegan", "gluten free", "ketogenic"],
        key="diet_type"
    )

    st.markdown("---")

@st.cache_data(ttl=3600)
def search_recipes(query, max_prep, number_results, diet):
    try:
        url = "https://api.spoonacular.com/recipes/complexSearch"

        params = {
            "query": query,
            "number": number_results,
            "addRecipeInformation": True,
            "addRecipeNutrition": True,
            "fillIngredients": True,
            "maxReadyTime": max_prep,
            "apiKey": get_spoonacular_key()
        }

        if diet != "None":
            params["diet"] = diet

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 401:
            return None, "401"
        if response.status_code == 404:
            return None, "404"
        if response.status_code == 429:
            return None, "429"
        if response.status_code >= 500:
            return None, "500"

        data = response.json()

        if not data.get("results"):
            return None, "empty"

        return data["results"], "ok"

    except requests.exceptions.Timeout:
        return None, "timeout"
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600)
def generate_description(recipe, query):
    try:
        genai.configure(api_key=get_gemini_key())
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        # Technique 1: Structured output — enforces exact 3-sentence format and scope rules
        # Technique 2: Few-shot — two examples anchor the tone and sentence structure
        prompt = f"""You are a recipe description assistant.

RULES:
- Write EXACTLY 3 sentences
- Do NOT include ingredients or measurements
- Do NOT add greetings or personality
- Keep tone neutral and app-like

Sentence 1: what the dish is
Sentence 2: why it's good for students
Sentence 3: taste/texture description

Examples:
User search: pasta
Recipe title: Spaghetti Aglio e Olio
Description: Spaghetti Aglio e Olio is a classic Italian pasta dish finished with olive oil and garlic. It comes together in under 20 minutes making it ideal for busy class nights. The result is silky and savory with a mild garlicky warmth.

User search: soup
Recipe title: Tomato Basil Soup
Description: Tomato Basil Soup is a smooth, blended soup with a bright tomato base. It reheats well and pairs with a sandwich for an easy dorm-friendly meal. The flavor is tangy and slightly sweet with a fresh herbal finish.

Now describe this recipe:
User search: {query}

Recipe:
{recipe}
"""

        return model.generate_content(prompt).text

    except Exception as e:
        return f"Gemini error: {e}"

st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
    background: {BG};
    color: {TEXT};
}}

.stApp {{
    background: {BG};
}}

.stButton > button {{
    background: {PRIMARY};
    color: white;
    border-radius: 10px;
}}

.stButton > button:hover {{
    background: {DARK};
}}
</style>
""", unsafe_allow_html=True)

st.title("Recipe Finder")

search_query = st.text_input("Search recipes...", key="search_query")

st.subheader("Recipe Suggestions")

if not search_query or search_query.strip() == "":
    st.warning("Please enter a recipe search term.")
    st.stop()

if len(search_query) > 2000:
    st.warning("Your search is very long (over 2000 characters). Consider shortening it for better results.")

st.toast("Searching recipes...")

with st.status("Fetching recipes...", expanded=False) as status:

    status.update(label="Calling Spoonacular API...")

    recipes, status_code = search_recipes(
        search_query,
        max_prep,
        number_results,
        diet
    )

    status.update(label="Processing results...")

if status_code == "401":
    st.error("API key invalid.")
elif status_code == "404":
    st.error("No results found.")
elif status_code == "429":
    st.error("Rate limit exceeded.")
elif status_code == "500":
    st.error("Server error.")
elif status_code == "timeout":
    st.error("Connection timeout.")
elif status_code == "empty":
    st.warning("No recipes found.")

elif status_code == "ok":

    filtered_recipes = []

    for r in recipes:
        nutrients = r.get("nutrition", {}).get("nutrients", [])

        calories = None
        for n in nutrients:
            if n.get("name") == "Calories":
                calories = n.get("amount")

        if calories is None or calories <= max_calories:
            r["calories"] = calories
            filtered_recipes.append(r)

    recipes = filtered_recipes

    st.success("Recipes found!")
    st.toast("Recipes loaded successfully!")

    df = pd.DataFrame([
        {
            "title": r["title"],
            "calories": r.get("calories", 0)
        }
        for r in recipes
    ])

    df = df.dropna()

    st.subheader("Calories per Recipe")
    st.bar_chart(df.set_index("title")["calories"])

    for r in recipes:

        st.markdown(f"""
### {r['title']}
⏱ Prep Time: {r.get('readyInMinutes', 'N/A')} min  
Calorie Amount: {r.get('calories', 'N/A')}
""")

        if r.get("image"):
            st.image(r["image"], width=200)

        with st.spinner("Generating description..."):
            description = generate_description(r, search_query)

        st.markdown("Description")
        st.write(description)

        ingredients = r.get("extendedIngredients", [])

        if ingredients:
            ingredient_text = " • ".join(
                [
                    (ing.get("original") or ing.get("name"))
                    for ing in ingredients
                    if ing.get("original") or ing.get("name")
                ]
            )

            st.markdown("Ingredients:")

            st.markdown(
                f"""
                <div style="
                    background:{CREAM};
                    padding:10px 12px;
                    border-radius:10px;
                    line-height:1.6;
                    font-size:13px;
                ">
                    {ingredient_text}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.caption("No ingredients available.")

        st.markdown("---")

else:
    st.info("Search for a recipe to get results.")
