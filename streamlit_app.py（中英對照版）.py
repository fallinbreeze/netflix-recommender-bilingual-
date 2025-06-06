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
    "How much time do you have? / 今天有多少時間可以看NetFlix？",
    ["< 1 hour", "Around 1 hour", "> 2 hours"]
)

kid_choice = st.radio(
    "Kids watching? / 有未滿18歲兒童/青少年一起觀看嗎？",
    ["Yes", "No"]
)

# --- Mood-Based Quiz ---
st.header("🧠 Mood Quiz / 電影心情指數測驗")

questions = [
    "1. How do you like feel vibes? / 你想要的氛圍？",
    "2. Current energy level? / 精神狀態？",
    "3. Preferred drink now? / 此刻想喝的？"
]

options = [
    ["Just chilling / 躺在沙發耍廢 不想動腦",
     "Exciting and intense / 來點刺激的體驗 讓心跳加快",
     "Deep and thoughtful / 內心平靜 整個世界都很寧靜",
     "Fun and cheerful / 我是一隻快樂小狗"],

    ["3% battery – save me / 沒電了 只想開啟省電模式",
     "Energy drink mode / 草上飛呀 感覺精神抖擻",
     "Balanced and calm / 像是進入 無我狀態般安定",
     "Need comfort / 哭哭 情緒低落想要拍拍"],

    ["Hot cocoa / 暖暖的巧克力熱飲",
     "Black coffee / 雅致的黑咖啡",
     "Soda / 快樂肥宅水",
     "Wine or cocktail / 微醺酒精感覺輕飄飄"]
]

answers = []
for i in range(3):
    answers.append(st.radio(questions[i], options[i], key=f"q{i}"))

# --- Genre Selection ---
st.header("🎯 Genre Preference / 類型偏好")
genre_options = {
    "None – Recommend by mood / 沒有特殊指定，依照分析結果推薦片單": None,
    "Comedy / 喜劇片": ["Comedies", "Family"],
    "Horror / Thriller / 恐怖驚悚片": ["Horror", "Thriller"],
    "Documentary / 紀錄片": ["Documentary"],
    "Action / Adventure / 動作冒險片": ["Action", "Adventure"],
    "Mystery / Crime / 懸疑犯罪片": ["Crime", "Mystery"],
    "Romantic / Drama / 愛情劇情片": ["Romantic", "Drama"]
}
genre_choice = st.selectbox("Pick a genre / 想看哪種類型？", list(genre_options.keys()))

# --- Determine mood ---
if genre_choice.startswith("None"):
    if answers.count(options[0][0]) >= 2:
        mood = "Chill Mode – Comedy / 只想耍廢放空 — 輕鬆喜劇"
        genres = ["Comedies", "Family"]
    elif answers.count(options[0][1]) >= 2:
        mood = "Thrill Seeker – Action / 尖叫有助於壓力釋放 — 冒險動作片"
        genres = ["Action", "Thriller", "Horror"]
    elif answers.count(options[0][2]) >= 2:
        mood = "Deep Thinker – Documentary / 老靈魂的深度探索 — 真實紀錄片"
        genres = ["Documentary"]
    elif answers.count(options[0][3]) >= 2:
        mood = "Dopamine Hunter – Romance / 給大腦補充多巴胺 — 浪漫愛情片"
        genres = ["Romantic", "Drama"]
    else:
        mood = "Dark Twist – Thriller / 越看越怕越想越毛 — 恐怖驚悚片"
        genres = ["Horror", "Thriller"]
else:
    mood = "Custom Genre Selected / 你指定想看的類型"
    genres = genre_options[genre_choice]

# --- Filtering Logic ---
if time_choice == "< 1 hour":
    df_filtered = df[df["duration_min"] <= 40]
elif time_choice == "Around 1 hour":
    df_filtered = df[(df["duration_min"] >= 30) & (df["duration_min"] <= 100)]
else:
    df_filtered = df[df["duration_min"] >= 80]

if kid_choice == "Yes":
    excluded = ["Horror", "Thriller", "Crime"]
    df_filtered = df_filtered[~df_filtered["genre_list"].apply(
        lambda g: any(tag in g for tag in excluded) if isinstance(g, list) else False)]

# --- Phase 1: 精準推薦（時間 + 心理 genre + 小孩條件）
df_phase1 = df_filtered[df_filtered["genre_list"].apply(
    lambda g: any(tag in g for tag in genres))] if genres else df_filtered

# --- Phase 2: 移除小孩條件（時間 + genre）
df_phase2 = df[df["duration_min"].between(df_filtered["duration_min"].min(), df_filtered["duration_min"].max())]
df_phase2 = df_phase2[df_phase2["genre_list"].apply(
    lambda g: any(tag in g for tag in genres))] if genres else df_phase2

# --- Phase 3: 只看時間條件
fallback_df = df[df["duration_min"].between(df_filtered["duration_min"].min(), df_filtered["duration_min"].max())]

# --- Display ---
st.subheader(f"🎭 Your Mood: {mood}")
st.write("Here are your personalized recommendations / 以下是你的推薦片單：")

if not df_phase1.empty:
    recommended = df_phase1.sample(min(5, len(df_phase1)), random_state=42)
elif not df_phase2.empty:
    st.info("Relaxed filters: Ignoring kids setting / 已放寬孩童模式條件")
    recommended = df_phase2.sample(min(5, len(df_phase2)), random_state=43)
elif not fallback_df.empty:
    st.info("Fallback to general timing match / 回到時間匹配模式")
    recommended = fallback_df.sample(min(5, len(fallback_df)), random_state=44)
else:
    st.error("😵 Still no fallback suggestions found. Try changing your mood or genre.")
    recommended = pd.DataFrame()

for _, row in recommended.iterrows():
    st.markdown(f"**📌 {row['title_zh']} ({row['title_en']})**")
    st.markdown(f"🗓️ {row['release_year']}｜{row['listed_in_zh_en']}｜{row['rating']}｜⏱️ 約 {row['duration_min']} 分鐘")
    st.markdown(f"{row['description']}")
    st.markdown("---")
