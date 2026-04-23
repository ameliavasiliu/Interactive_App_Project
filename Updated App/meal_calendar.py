import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar

# Page
st.set_page_config(page_title="Calendar | Hoos Hungry?", layout="centered")

# Session State
if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = []

if "month" not in st.session_state:
    st.session_state.month = 3

if "year" not in st.session_state:
    st.session_state.year = 2024

# Colors
PRIMARY = "#8fa98c"
DARK = "#4a7a50"
BG = "#b8ccb5"
TEXT = "#1a1a1a"
CREAM = "#f5f1e6"

# CSS
st.markdown(f"""
<style>

.block-container {{
    padding-top: 0rem !important;
}}

header {{
    visibility: hidden;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    font-family: 'Nunito', sans-serif !important;
}}

.app-card {{
    background: white;
    border-radius: 18px;
    padding: 14px 18px 18px 18px;
    margin-top: 0px;
}}

.header {{
    display: flex;
    justify-content: center;
    margin-top: 18px;
    margin-bottom: 12px;
}}

.title {{
    background: {PRIMARY};
    padding: 10px 22px;
    border-radius: 12px;
    font-size: 22px;
    font-weight: 900;
}}

.weekdays {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 10px;
    color: {TEXT};
}}

.cell-wrap {{
    padding: 4px;
}}

.day {{
    min-height: 85px;
    border-radius: 14px;
    padding: 8px;
    background: {PRIMARY};
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.day.has-meal {{
    background: {DARK};
}}

.day-num {{
    font-size: 12px;
    font-weight: 800;
}}

.meal {{
    font-size: 10px;
    line-height: 1.3;
}}

/* ✅ REMOVED CREAM BAR */
.calendar-wrap {{
    background: transparent;   /* was cream */
    padding: 0;
    margin-top: 0;
}}

.week-card, .day-card {{
    background: {CREAM};
    padding: 16px;
    border-radius: 16px;
    margin-top: 10px;
    border: 2px solid #e6dfcf;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 10px;
    background: {CREAM};
    padding: 8px;
    border-radius: 14px;
}}

.stTabs [data-baseweb="tab"] {{
    background: white;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 700;
}}

.stTabs [aria-selected="true"] {{
    background: {PRIMARY} !important;
    color: white !important;
}}

</style>
""", unsafe_allow_html=True)

# Data
@st.cache_data
def base_meals():
    return {
        1: ["Oatmeal"],
        3: ["Butter Chickpeas"],
        5: ["Caesar Wrap"],
        7: ["Samosas", "Greek Salad"],
        10: ["Burrito Bowl"],
        12: ["Fettuccine Alfredo"],
        15: ["Avocado Toast", "Lentil Soup"],
        18: ["Mushroom Pasta"],
        20: ["Veggie Stir Fry"],
        22: ["Caesar Wrap"],
        25: ["Butter Chickpeas"],
        28: ["Pesto Sandwich"],
        30: ["Lentil Soup"],
    }

def get_meals(month, year):
    data = base_meals().copy()

    for m in st.session_state.saved_meals:
        d = datetime.strptime(m["date"], "%Y-%m-%d")
        if d.month == month and d.year == year:
            data.setdefault(d.day, []).append(m["name"])

    return data

# Title
st.title("📅 Calendar")

tab1, tab2, tab3 = st.tabs(["Month", "Week", "Day"])

# Month View
with tab1:

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        a1, a2 = st.columns([1, 1])

        with a1:
            if st.button("⬅️"):
                if st.session_state.month == 1:
                    st.session_state.month = 12
                    st.session_state.year -= 1
                else:
                    st.session_state.month -= 1

        with a2:
            if st.button("➡️"):
                if st.session_state.month == 12:
                    st.session_state.month = 1
                    st.session_state.year += 1
                else:
                    st.session_state.month += 1

    month = st.session_state.month
    year = st.session_state.year

    meals = get_meals(month, year)
    cal = calendar.monthcalendar(year, month)

    st.markdown('<div class="app-card">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="header">
        <div class="title">{calendar.month_name[month]} {year}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="weekdays">
        <div>Mon</div><div>Tue</div><div>Wed</div>
        <div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div>
    </div>
    """, unsafe_allow_html=True)

    for week in cal:
        cols = st.columns(7)

        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown('<div class="cell-wrap"></div>', unsafe_allow_html=True)
                else:
                    day_meals = meals.get(day, [])
                    has = len(day_meals) > 0
                    meal_text = "<br>".join(day_meals[:2])

                    st.markdown(f"""
                    <div class="cell-wrap">
                        <div class="day {'has-meal' if has else ''}">
                            <div class="day-num">{day}</div>
                            <div class="meal">{meal_text}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Week View
with tab2:
    month = st.session_state.month
    year = st.session_state.year
    meals = get_meals(month, year)

    cal = calendar.monthcalendar(year, month)

    week_index = st.selectbox("Select Week", list(range(1, len(cal) + 1))) - 1
    week = cal[week_index]

    st.markdown('<div class="week-card">', unsafe_allow_html=True)

    cols = st.columns(7)

    for i, day in enumerate(week):
        with cols[i]:
            if day == 0:
                st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)
            else:
                day_meals = meals.get(day, [])
                has = len(day_meals) > 0

                meal_html = "<br>".join([f"🍽 {m}" for m in day_meals]) if day_meals else "<span style='opacity:0.5'>—</span>"

                st.markdown(f"""
                <div style="
                    background:{'#4a7a50' if has else '#8fa98c'};
                    border-radius:14px;
                    padding:10px;
                    min-height:90px;
                    color:white;
                    text-align:center;
                ">
                    <div style="font-weight:800; font-size:12px;">
                        {calendar.day_abbr[i]}
                    </div>
                    <div style="font-size:11px; margin-bottom:6px;">
                        {day}
                    </div>
                    <div style="font-size:10px; line-height:1.3;">
                        {meal_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Day View
with tab3:
    selected = st.date_input(
        "Pick a day",
        date(st.session_state.year, st.session_state.month, 1)
    )

    meals = get_meals(selected.month, selected.year).get(selected.day, [])

    st.markdown('<div class="day-card">', unsafe_allow_html=True)

    st.subheader(selected.strftime("%B %d"))

    if meals:
        for m in meals:
            st.success(f"🍽 {m}")
    else:
        st.warning("No meals planned.")

    st.markdown('</div>', unsafe_allow_html=True)

# Add Meal
st.markdown("### ➕ Add Meal")

c1, c2 = st.columns(2)

with c1:
    meal_date = st.date_input("Date", key="add_date")

with c2:
    meal_type = st.selectbox("Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

meal_name = st.text_input("Meal name")

if st.button("Add Meal"):
    if meal_name.strip():
        st.session_state.saved_meals.append({
            "date": str(meal_date),
            "type": meal_type,
            "name": meal_name
        })
        st.rerun()

if st.session_state.saved_meals:
    st.write("**Your planned meals:**")
    st.dataframe(pd.DataFrame(st.session_state.saved_meals), use_container_width=True)