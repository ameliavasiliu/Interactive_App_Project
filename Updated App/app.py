import streamlit as st

#  Page config 
st.set_page_config(page_title="Hoos Hungry?", layout="centered", initial_sidebar_state="collapsed")

# Session state defaults 
if "dietary_prefs" not in st.session_state:
    st.session_state.dietary_prefs = []
if "notifications_on" not in st.session_state:
    st.session_state.notifications_on = True
if "username" not in st.session_state:
    st.session_state.username = "UVA Student"
if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = []
if "meal_ratings" not in st.session_state:
    st.session_state.meal_ratings = {
        "Butter Chickpeas": 4,
        "Caesar Wrap": 5,
        "Samosas": 3,
    }

# Shared CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #b8ccb5 !important;
    font-family: 'Nunito', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: #b8ccb5 !important;
    padding-bottom: 100px !important;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { background: #7a9e7e !important; }
header[data-testid="stHeader"] { background: #7a9e7e !important; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebarNav"] { display: block !important; }
[data-testid="stSidebarCollapsedControl"] { display: block !important; }
[data-testid="stCaptionContainer"] p { color: black !important; }

.hh-header {
    background: #7a9e7e; padding: 22px 20px 18px;
    margin: -1rem -1rem 0; text-align: center;
}
.hh-header h1 { font-size: 2.4rem; font-weight: 900; color: #1a1a1a; letter-spacing: -1px; }

div[data-testid="stButton"] > button {
    background: #6b6b6b !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 700 !important;
}
div[data-testid="stButton"] > button:hover { background: #4a7a50 !important; }
</style>
""", unsafe_allow_html=True)

#  Header 
st.markdown('<div class="hh-header"><h1>Hoos Hungry?</h1></div>', unsafe_allow_html=True)
st.write("")

#  Help & Support
with st.expander("📋  Help & Support"):
    st.info("**FAQs**\n\n"
            "- How do I add a meal? → Go to the Calendar page.\n"
            "- How do I find recipes? → Visit the Recipe Finder page.\n"
            "- How do I save a meal? → Visit the Saved Meals page.\n"
            "- How do I set dietary preferences? → Settings → Meal Preferences.")
    st.write("Contact: **hoos-hungry@virginia.edu**")

#  Notifications 
with st.expander("🔔  Notifications"):
    # Widget 1: toggle notifications on/off
    # key="notif_toggle" — stable identity across reruns; ensures session state
    # persists correctly when other expanders are opened/closed
    notif = st.toggle("Enable meal reminders", value=st.session_state.notifications_on, key="notif_toggle")
    st.session_state.notifications_on = notif
    if notif:
        # Widget 2: selectbox for reminder time — only visible when notifications are ON
        # This is a Dynamic UI pattern: reminder time control only appears when meaningful
        times = ["7:00 AM", "8:00 AM", "12:00 PM", "6:00 PM", "7:00 PM"]
        chosen_time = st.selectbox("Reminder time", times, key="reminder_time_select")
        st.write(f"✅ Reminders set for **{chosen_time}** daily.")
    else:
        st.warning("⚠️ Meal reminders are currently off.")

#  Account Details 
with st.expander("👤  Account Details"):
    # Widget 3: text input for display name
    new_name = st.text_input("Display name", value=st.session_state.username, key="username_input")
    if st.button("Save name", key="save_name_btn"):
        st.session_state.username = new_name
        st.write(f"✅ Name updated to **{new_name}**!")

#  Meal Preferences & Planning 
with st.expander("🥗  Meal Preferences & Planning"):
    # Widget 4: multiselect for dietary restrictions
    # key="diet_prefs" — required so saved state survives page navigation and reruns
    options = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free", "Halal", "Kosher"]
    prefs = st.multiselect("Dietary restrictions", options,
                           default=st.session_state.dietary_prefs, key="diet_prefs")
    st.session_state.dietary_prefs = prefs

    # Widget 5: slider for max prep time preference
    max_prep = st.slider("Max preferred prep time (minutes)", 5, 60, 30, key="max_prep_slider")

    if st.button("Save preferences", key="save_prefs_btn"):
        msg = f"✅ Saved! Showing meals under **{max_prep} min** prep"
        if prefs:
            msg += f" · Filters: {', '.join(prefs)}"
        st.success(msg)