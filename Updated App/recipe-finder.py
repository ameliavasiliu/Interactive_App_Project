import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# Color Scheme
PRIMARY = "#8fa98c"
DARK = "#4a7a50"
BG = "#b8ccb5"
TEXT = "#1a1a1a"
CREAM = "#f5f1e6"

# Page
st.set_page_config(
    page_title="Recipe Finder | Hoos Hungry?",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Session State Default
if "sort_sel" not in st.session_state:
    st.session_state.sort_sel = "Rating ↓"

# API Key
def get_gemini_key():
    return st.secrets["api"]["GEMINI_API_KEY"]

# Gemini Search
@st.cache_data(ttl=3600)
def search_recipes(query):
    try:
        api_key = get_gemini_key()
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("models/gemini-2.5-flash")

        prompt = f"""
        Give me 5 recipes for: {query}.

        For each recipe include:
        - Title
        - Calories estimate
        - Prep time
        - Short description
        """

        response = model.generate_content(prompt)
        return response.text, "ok"

    except KeyError:
        return None, "missing_key"
    except Exception as e:
        return None, str(e)

# Local Data
@st.cache_data
def load_recipe_data():
    data = {
        "Name": [
            "Butter Chickpeas", "Mushroom Pasta", "Burrito Bowl",
            "Fettuccine Alfredo", "Caesar Wrap"
        ],
        "Category": ["Dinner", "Dinner", "Lunch", "Dinner", "Lunch"],
        "Calories": [450, 520, 610, 720, 480],
        "Prep Time (min)": [30, 25, 20, 35, 10],
        "Rating": [4.5, 4.2, 4.7, 4.1, 4.8],
    }
    return pd.DataFrame(data)

df = load_recipe_data()

# Aesthetic
st.markdown(f"""
<style>

html, body, [data-testid="stAppViewContainer"] {{
    background: {BG};
    color: {TEXT};
}}

.stApp {{
    background: {BG};
    color: {TEXT};
}}

.stTextInput > div > div > input {{
    background: {CREAM};
    color: {TEXT};
}}

.stDataFrame {{
    background: {CREAM};
}}

.stButton > button {{
    background: {PRIMARY};
    color: white;
    border-radius: 10px;
    border: none;
}}

.stButton > button:hover {{
    background: {DARK};
}}

h1, h2, h3 {{
    color: {TEXT};
}}

</style>
""", unsafe_allow_html=True)

# UI
st.title("🔍 Recipe Finder")

search_query = st.text_input("Search recipes...")

# Local Filtering
filtered = df.copy()

if search_query:
    filtered = filtered[
        filtered["Name"].str.contains(search_query, case=False, na=False)
    ]

# Advanced Filters
show_adv = st.toggle("Show Advanced Filters")

if show_adv:
    st.subheader("🎛️ Advanced Filters")

    cal_range = st.slider("Calories", 200, 800, (200, 800))
    max_prep = st.slider("Max Prep Time (min)", 5, 60, 60)

    filtered = filtered[
        (filtered["Calories"] >= cal_range[0]) &
        (filtered["Calories"] <= cal_range[1]) &
        (filtered["Prep Time (min)"] <= max_prep)
    ]

# Sorting
sort_map = {
    "Rating ↓": ("Rating", False),
    "Calories ↑": ("Calories", True),
    "Prep Time ↑": ("Prep Time (min)", True)
}

sort_col, sort_asc = sort_map[st.session_state.sort_sel]
filtered = filtered.sort_values(sort_col, ascending=sort_asc)

# Display
st.subheader("📊 Recipes")

if filtered.empty:
    st.warning("No recipes match your filters.")
else:
    st.dataframe(filtered, use_container_width=True)

    if show_adv and not filtered.empty:
        fig = px.scatter(
            filtered,
            x="Prep Time (min)",
            y="Calories",
            size="Rating",
            color="Category",
            text="Name"
        )
        st.plotly_chart(fig, use_container_width=True)

# Gemini Output
st.subheader("🤖 AI Recipe Suggestions")

if search_query:
    with st.spinner("Generating recipes..."):
        api_results, api_status = search_recipes(search_query)

    if api_status == "missing_key":
        st.error("Missing GEMINI_API_KEY in secrets.toml")
    elif api_status == "ok":
        st.write(api_results)
    else:
        st.error(f"Error: {api_status}")
else:
    st.info("Search for a recipe to get AI suggestions.")