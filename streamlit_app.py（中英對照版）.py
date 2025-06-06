# netflix_streamlit_fallback.py

import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- Load data ---
@st.cache_data

def load_data():
    df = pd.read_csv("netflix_bilingual_merged_clean.csv")
    if isinstance(df.loc[0, "genre_list"], str):
        df["genre_list"] = df["genre_list"].apply(eval)
    return df

df = load_data()

# --- Title ---
st.title("🎬 Netflix Viewing Mood Recommender / 電影人格推薦")
st.markdown("Find the perfect show based on your current mood and time 🎧🍿")

# --- User Preferences ---
st.header("📋 Preferences / 偏好設定")

time_choice = st.selectbox(
    "How much time do you have? / 今天打算看多久？",
    ["< 1 hour", "Around 1 hour", "> 2 hours"]
)

kid_choice = st.radio(
    "Kids watching? / 有小孩一起觀看嗎？",
    ["Yes", "No"]
)

# --- Mood-Based Quiz ---
st.header("🧠 Mood Quiz / 心情測驗")

questions = [
    "1. What do you feel like doing? / 你現在想做什麼？",
    "2. Current energy level? / 精神狀態？",
    "3. Preferred drink now? / 此刻想喝的？"
]

options = [
    ["Just chilling / 放空耍廢",
     "Exciting and intense / 刺激熱血",
     "Deep and thoughtful / 發人深省",
     "Fun and cheerful / 輕鬆愉快"],

    ["3% battery – save me / 精力枯竭",
     "Energy drink mode / 精神抖擻",
     "Balanced and calm / 平靜放鬆",
     "Need comfort / 情緒低落"],

    ["Hot cocoa / 巧克力熱飲",
     "Black coffee / 黑咖啡",
     "Soda / 汽水果汁",
     "Wine or cocktail / 微醺酒感"]
]

answers = []
for i in range(3):
    answers.append(st.radio(questions[i], options[i], key=f"q{i}"))

# --- Genre Selection ---
st.header("🎯 Genre Preference / 類型偏好")
genre_options = {
    "None – Recommend by mood / 不指定，依分析結果推薦": None,
    "Comedy / 喜劇": ["Comedies", "Family"],
    "Horror / Thriller / 恐怖驚悚": ["Horror", "Thriller"],
    "Documentary / 紀錄片": ["Documentary"],
    "Action / Adventure / 動作冒險": ["Action", "Adventure"],
    "Mystery / Crime / 懸疑犯罪": ["Crime", "Mystery"],
    "Romantic / Drama / 愛情劇情": ["Romantic", "Drama"]
}
genre_choice = st.selectbox("Pick a genre / 想看哪種類型？", list(genre_options.keys()))

# --- Determine mood ---
if genre_choice.startswith("None"):
    if answers.count(options[0][0]) >= 2:
        mood = "Chill Mode – Comedy / 耍廢喜劇模式"
        genres = ["Comedies", "Family"]
    elif answers.count(options[0][1]) >= 2:
        mood = "Thrill Seeker – Action / 刺激冒險模式"
        genres = ["Action", "Thriller", "Horror"]
    elif answers.count(options[0][2]) >= 2:
        mood = "Deep Thinker – Documentary / 沉思紀實模式"
        genres = ["Documentary"]
    elif answers.count(options[0][3]) >= 2:
        mood = "Dopamine Hunter – Romance / 情感療癒模式"
        genres = ["Romantic", "Drama"]
    else:
        mood = "Dark Twist – Thriller / 黑暗曲線模式"
        genres = ["Horror", "Thriller"]
else:
    mood = "Custom Genre Selected / 使用者自選類型"
    genres = genre_options[genre_choice]

# --- Filtering Logic ---
if time_choice == "< 1 hour":
    df_filtered = df[df["duration_min"] <= 40]  # 稍放寬限制
elif time_choice == "Around 1 hour":
    df_filtered = df[(df["duration_min"] >= 30) & (df["duration_min"] <= 100)]
else:
    df_filtered = df[df["duration_min"] >= 80]

if kid_choice == "Yes":
    excluded = ["Horror", "Thriller", "Crime"]
    df_filtered = df_filtered[~df_filtered["genre_list"].apply(
        lambda g: any(tag in g for tag in excluded) if isinstance(g, list) else False)]

# 篩選類型
if genres:
    df_filtered = df_filtered[df_filtered["genre_list"].apply(
        lambda g: any(tag in g for tag in genres))]

# --- Display Results ---
st.subheader(f"🎭 Your Mood: {mood}")
st.write("Here are your personalized recommendations / 以下是你的推薦片單：")

if not df_filtered.empty:
    recommended = df_filtered.sample(min(5, len(df_filtered)), random_state=42)
    for _, row in recommended.iterrows():
        st.markdown(f"**📌 {row['title_zh']} ({row['title_en']})**")
        st.markdown(f"🗓️ {row['release_year']}｜{row['listed_in_zh_en']}｜{row['rating']}｜⏱️ 約 {row['duration_min']} 分鐘")
        st.markdown(f"{row['description']}")
        st.markdown("---")
else:
    st.warning("😥 No matches found. Here's a relaxed fallback:")
    fallback = df[df["genre_list"].apply(lambda g: any(tag in g for tag in genres))]
    if not fallback.empty:
        relaxed = fallback.sample(min(5, len(fallback)), random_state=0)
        for _, row in relaxed.iterrows():
            st.markdown(f"**📌 {row['title_zh']} ({row['title_en']})**")
            st.markdown(f"🗓️ {row['release_year']}｜{row['listed_in_zh_en']}｜{row['rating']}｜⏱️ 約 {row['duration_min']} 分鐘")
            st.markdown(f"{row['description']}")
            st.markdown("---")
    else:
        st.error("😵 Still no fallback suggestions found. Try changing your mood or genre.")
