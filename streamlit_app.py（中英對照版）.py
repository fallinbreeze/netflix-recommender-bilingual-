# streamlit_bilingual_app.py
import streamlit as st
import pandas as pd
import random

# --- Load Data ---
@st.cache_data

def load_data():
    df = pd.read_csv("netflix_bilingual_merged_clean.csv")
    if isinstance(df.loc[0, "genre_list"], str):
        df["genre_list"] = df["genre_list"].apply(eval)
    return df

df = load_data()

# --- Title ---
st.title("🎬 Netflix 観影人格推薦系統 | Mood-Based Recommender")
st.markdown("請根據您的心情與觀影時間，獲得專屬推薦片單 | Get a personalized list based on your mood and time 🎧🍿")

# --- User Preferences ---
st.header("📋 基本偏好設定 | User Preferences")

time_choice = st.selectbox(
    "您今天有多少時間觀影？| How much time do you have?",
    ["少於 1 小時 | < 1 hour", "大約 1 小時 | Around 1 hour", "超過 2 小時 | > 2 hours"]
)

kid_choice = st.radio(
    "今天會有小朋友一起觀賞嗎？| Are there kids watching with you?",
    ["是 | Yes", "否 | No"]
)

# --- Mood Quiz ---
st.header("🧠 心情測驗 | Mood Quiz")

questions = [
    "Q1. 現在最想做什麼？| What do you feel like doing?",
    "Q2. 您目前的能量程度？| What is your energy level?",
    "Q3. 如果現在來一杯飲料，會想喝什麼？| What would you drink now?"
]

options = [
    ["躺平放空不動腦 | Chilling, no brain needed",
     "刺激緊張感爆棚 | Thrilling action",
     "來點深度思考哲學感 | Deep and thoughtful",
     "療癒開心開懷笑 | Cheerful and fun"],

    ["電量剩 3% 省電模式 | Low battery",
     "剛喝完能量飲料超亢奮 | Hyper mode",
     "一半一半中性平靜 | Balanced",
     "有點失落想被安慰 | Feeling low"],

    ["熱可可 / 奶茶 | Hot cocoa / Milk tea",
     "黑咖啡 | Black coffee",
     "果汁 / 汽水 | Juice / Soda",
     "紅酒 / 調酒 | Wine / Cocktail"]
]

answers = []
for i in range(3):
    answers.append(st.radio(questions[i], options[i], key=f"q{i}"))

# --- Genre Choice ---
st.header("🎯 指定類型偏好 | Genre Preference")
genre_options = {
    "無指定，依心情推薦 | No Preference": None,
    "喜劇 | Comedy": ["Comedies", "Family"],
    "恐怖 / 驚悚 | Horror / Thriller": ["Horror", "Thriller"],
    "紀錄片 | Documentary": ["Documentary"],
    "動作 / 冒險 | Action / Adventure": ["Action", "Adventure"],
    "懸疑 / 犯罪 | Mystery / Crime": ["Crime", "Mystery"],
    "浪漫 / 劇情 | Romance / Drama": ["Romantic", "Drama"]
}
genre_choice = st.selectbox("想看特定類型嗎？| Pick a genre?", list(genre_options.keys()))

# --- Determine Mood ---
if genre_choice == "無指定，依心情推薦 | No Preference":
    if answers.count(options[0][0]) >= 2:
        mood = "放空耍廢模式 Chill Mode"
        genres = ["Comedies", "Family"]
    elif answers.count(options[0][1]) >= 2:
        mood = "刺激系觀眾 Thrill Seeker"
        genres = ["Action", "Thriller", "Horror"]
    elif answers.count(options[0][2]) >= 2:
        mood = "深度思考型 Deep Thinker"
        genres = ["Documentary"]
    elif answers.count(options[0][3]) >= 2:
        mood = "療癒戀愛派 Dopamine Hunter"
        genres = ["Romantic", "Drama"]
    else:
        mood = "黑暗陰鬱風格 Dark Twist"
        genres = ["Horror", "Thriller"]
else:
    mood = "自訂類型 Custom Genre"
    genres = genre_options[genre_choice]

# --- Filtering Logic ---
if "少於" in time_choice:
    df_filtered = df[df["duration_min"] <= 30]
elif "大約" in time_choice:
    df_filtered = df[(df["duration_min"] > 30) & (df["duration_min"] <= 90)]
else:
    df_filtered = df[df["duration_min"] > 90]

if "是" in kid_choice:
    excluded = ["Horror", "Thriller", "Crime"]
    df_filtered = df_filtered[~df_filtered["genre_list"].apply(
        lambda g: any(tag in g for tag in excluded) if isinstance(g, list) else False)]

# 篩選類型
if genres:
    df_filtered = df_filtered[df_filtered["genre_list"].apply(
        lambda g: any(tag in g for tag in genres))]

# --- Show Result ---
st.subheader(f"🎭 你的觀影人格 | Your Mood: {mood}")
st.write("以下是為你量身推薦的片單 | Here are some shows we recommend for you:")

if not df_filtered.empty:
    recommended = df_filtered.sample(min(5, len(df_filtered)), random_state=42)
    for i, row in recommended.iterrows():
        st.markdown(f"**📌 {row['title_zh']} ({row['title_en']})**")
        st.markdown(f"🗓️ {row['release_year']}｜{row['listed_in_zh_en']}｜{row['rating']}｜⏱️ 約 {row['duration_min']} 分鐘")
        st.markdown(f"{row['description']}")
        st.markdown("---")
else:
    st.warning("😢 查無符合的推薦內容 | No matching recommendations found.")
