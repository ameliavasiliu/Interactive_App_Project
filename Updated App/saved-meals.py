import streamlit as st
import pandas as pd
import plotly.express as px

# Page config 
st.set_page_config(page_title="Saved Meals | Hoos Hungry?", layout="centered", initial_sidebar_state="collapsed")

# Session state defaults 
if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = []
if "meal_ratings" not in st.session_state:
    st.session_state.meal_ratings = {
        "Butter Chickpeas": 4,
        "Caesar Wrap": 5,
        "Samosas": 3,
    }
if "dietary_prefs" not in st.session_state:
    st.session_state.dietary_prefs = []
if "username" not in st.session_state:
    st.session_state.username = "UVA Student"
# Rating form state
if "rate_meal_category" not in st.session_state:
    st.session_state.rate_meal_category = "All"
if "rate_meal_sel" not in st.session_state:
    st.session_state.rate_meal_sel = None
if "show_ratings_form" not in st.session_state:
    st.session_state.show_ratings_form = False

# CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #b8ccb5 !important;
    font-family: 'Nunito', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main { background: #b8ccb5 !important; padding-bottom: 60px !important; }
#MainMenu, footer{ visibility: hidden; }
[data-testid="stToolbar"] { background: #7a9e7e !important; }
header[data-testid="stHeader"] { background: #7a9e7e !important; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebarNav"] { display: block !important; }
[data-testid="stSidebarCollapsedControl"] { display: block !important; }
[data-testid="stCaptionContainer"] p { color: black !important; }

.profile-avatar-wrap { display: flex; flex-direction: column; align-items: center; padding: 20px 0 8px; }
.profile-avatar {
    width: 110px; height: 110px; border-radius: 50%;
    background: #b0b0b0; display: flex; align-items: center;
    justify-content: center; font-size: 3rem; margin-bottom: 8px;
}

div[data-testid="stButton"] > button {
    background: #6b6b6b !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
}
div[data-testid="stButton"] > button:hover { background: #4a7a50 !important; }
</style>
""", unsafe_allow_html=True)

# Cached recipe list for the rating selector
@st.cache_data
def load_recipe_names():
    """Return cached list of all recipe names with their category."""
    return {
        "Butter Chickpeas": "Dinner",
        "Mushroom Spinach Pasta": "Dinner",
        "Burrito Bowl": "Lunch",
        "Fettucine Alfredo": "Dinner",
        "Caesar Wrap": "Lunch",
        "Samosas": "Breakfast",
        "Cauliflower Rice & Zucchini": "Lunch",
        "Mozzarella Pesto Sandwich": "Lunch",
        "Avocado Toast": "Breakfast",
        "Greek Salad": "Lunch",
        "Lentil Soup": "Dinner",
        "Veggie Stir Fry": "Dinner",
    }

recipe_category_map = load_recipe_names()

# Callback: on_change for dependent dropdown
# on_change is needed because when Bob switches meal category (parent), we must clear the child meal selection
# a plain if-block can't clear session state before the widget is re-rendered, causing a stale mismatch
def on_rate_category_change():
    st.session_state.rate_meal_sel = None

# Callback: on_click — Reset ratings form 
# on_click is necessary to reset MULTIPLE form fields atomically (category,meal selection, star slider, visibility toggle) in one callback before the next render
# A plain if-block would only run after widgets are drawn, leaving stale values visible for one frame.
def reset_rating_form():
    st.session_state.rate_meal_category = "All"
    st.session_state.rate_meal_sel = None
    st.session_state.star_slider = 3
    st.session_state.show_ratings_form = False

# Profile avatar
st.markdown(f'''<div class="profile-avatar-wrap">
  <div class="profile-avatar">👤</div>
  <div style="font-size:1.2rem;font-weight:700">{st.session_state.username}</div>
</div>''', unsafe_allow_html=True)

# Layout primitive: st.columns for left / right panels
left_col, right_col = st.columns([1, 1.5])

with left_col:
    # Favorited Meals 
    st.markdown("**⭐ Favorited Meals**")
    favs = [m for m, r in st.session_state.meal_ratings.items() if r >= 4]
    if favs:
        for f in favs:
            st.write(f"• {f}")
    else:
        st.caption("No favorited meals yet.")

    st.write("")

    # Saved Meals 
    st.markdown("**🍽️ Saved Meals**")
    if st.session_state.saved_meals:
        for entry in st.session_state.saved_meals[-5:]:
            st.write(f"• {entry['name']} ({entry['type']})")
    else:
        st.caption("No saved meals yet.\nAdd meals from the Calendar page.")

    st.write("")

    # Dietary Preferences summary 
    st.markdown("**✏️ Dietary Preferences**")
    if st.session_state.dietary_prefs:
        st.write(", ".join(st.session_state.dietary_prefs))
    else:
        st.caption("None set. Go to Settings.")

with right_col:
    # Meal Ratings chart 
    st.markdown("**📊 Meal Ratings**")
    if st.session_state.meal_ratings:
        ratings_df = pd.DataFrame(
            list(st.session_state.meal_ratings.items()),
            columns=["Meal", "Stars"]
        ).sort_values("Stars", ascending=False)

        st.bar_chart(ratings_df.set_index("Meal")["Stars"], use_container_width=True)
        st.dataframe(ratings_df.reset_index(drop=True), use_container_width=True, hide_index=True)
    else:
        st.info("No ratings yet. Rate a meal below!")

# DYNAMIC UI #1: Show/hide the Rate a Meal form 
# The rating form is hidden by default to keep the page clean
# Bob can expand it when he wants to log a rating
# This avoids cluttering the profile view with a form Bob may not need on every visit
st.write("")
show_form = st.toggle(
    "⭐ Rate a Meal",
    value=st.session_state.show_ratings_form,
    key="show_ratings_form"  # key required: reset_rating_form() turns this off by key
)

if show_form:
    st.subheader("Rate a Meal")

    # DEPENDENT DROPDOWNS 
    # Parent dropdown: meal category — drives which recipes appear in child
    col_r0, col_r1, col_r2 = st.columns(3)
    with col_r0:
        # Widget: parent category selector
        # key required: on_change callback clears child selection by referencing this key
        rate_category = st.selectbox(
            "Category",
            ["All", "Breakfast", "Lunch", "Dinner"],
            key="rate_meal_category",        # key required: on_change needs this to fire correctly
            on_change=on_rate_category_change  # clears child when parent changes
        )

    # Build child options based on parent
    if rate_category == "All":
        meal_options = list(recipe_category_map.keys())
    else:
        meal_options = [m for m, c in recipe_category_map.items() if c == rate_category]

    # Resolve safe index for child
    current_sel = st.session_state.get("rate_meal_sel")
    default_idx = meal_options.index(current_sel) if current_sel in meal_options else 0

    with col_r1:
        # Child dropdown: specific meal — options depend on selected category above
        meal_to_rate = st.selectbox(
            "Choose meal",
            meal_options,
            index=default_idx,
            key="rate_meal_sel"  # key required: on_rate_category_change resets this by key
        )

    with col_r2:
        # Widget: star rating slider
        # key required: reset_rating_form() resets this to 3 by key
        star_rating = st.slider("Stars ⭐", 1, 5, 3, key="star_slider")

    col_submit, col_reset = st.columns([1, 1])
    with col_submit:
        if st.button("Submit Rating", key="submit_rating_btn"):
            st.session_state.meal_ratings[meal_to_rate] = star_rating
            st.success(f"✅ Rated **{meal_to_rate}**: {'⭐' * star_rating}")
            st.rerun()
    with col_reset:
        st.button("🔄 Clear Form", key="clear_rating_form_btn", on_click=reset_rating_form)

# Saved Meals full table 
st.write("")
st.subheader("📋 All Planned Meals")
if st.session_state.saved_meals:
    saved_df = pd.DataFrame(st.session_state.saved_meals)
    st.dataframe(saved_df, use_container_width=True)

    # Widget: filter saved meals by type
    filter_type = st.radio(
        "Filter by type", ["All", "Breakfast", "Lunch", "Dinner", "Snack"],
        horizontal=True, key="saved_filter_radio"  # key required for stable widget identity across reruns
    )
    if filter_type != "All":
        filtered_saved = saved_df[saved_df["type"] == filter_type]
        if filtered_saved.empty:
            st.warning(f"⚠️ No {filter_type} meals saved yet.")
        else:
            st.dataframe(filtered_saved.reset_index(drop=True), use_container_width=True)

    # DYNAMIC UI #2: Pie chart only visible when 2+ meal types exist 
    # Showing a pie chart with a single slice is meaningless. The chart section
    # (header + chart + caption) only renders when there are at least 2 distinct
    # meal types in the current filtered view, keeping the UI purposeful.
    pie_df = saved_df if filter_type == "All" else saved_df[saved_df["type"] == filter_type]
    type_counts = pie_df["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]

    if len(type_counts) >= 2:
        st.write("")
        st.subheader("🥧 Meal Type Breakdown")
        st.caption("Distribution of your planned meals by type · Updates when you add or clear meals")

        fig_pie = px.pie(
            type_counts,
            names="Type",
            values="Count",
            color="Type",
            color_discrete_map={
                "Breakfast": "#e8a87c",
                "Lunch": "#7a9e7e",
                "Dinner": "#4a7a50",
                "Snack": "#a8c5a0",
            },
            hole=0.35,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Nunito, sans-serif",
            showlegend=True,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    elif len(type_counts) == 1:
        st.caption(f"All planned meals are **{type_counts.iloc[0]['Type']}** — add more variety to see the breakdown chart.")

    if st.button("🗑️ Clear all saved meals", key="clear_meals_btn"):
        st.session_state.saved_meals = []
        st.success("✅ All saved meals cleared.")
        st.rerun()
else:
    st.info("No meals planned yet. Go to the Calendar page to add meals.")