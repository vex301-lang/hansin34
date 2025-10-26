# -*- coding: utf-8 -*-
import re
import streamlit as st
from openai import OpenAI

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="한신 초등 은유 이야기 기계", page_icon="✨")
st.title("✨ 한신 초등학교 친구들의 이야기 실력을 볼까요?")
st.caption("좋아하는 단어로 주인공을 만들고, 이야기를 이어가며 상상력을 펼쳐보아요!")

# OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# 금칙어 목록
# -----------------------------
BANNED_PATTERNS = [
    r"살인", r"죽이", r"폭력", r"피바다", r"학대", r"총", r"칼", r"폭탄",
    r"kill", r"murder", r"gun", r"knife", r"blood", r"assault", r"bomb",
    r"성\\s*행위", r"야동", r"포르노", r"음란", r"가슴", r"성기", r"자위",
    r"porn", r"sex", r"xxx", r"nude", r"naked",
]
BAN_RE = re.compile("|".join(BANNED_PATTERNS), re.IGNORECASE)

def words_valid(words):
    for w in words:
        if not w:
            return False, "단어 3개를 모두 입력해 주세요."
        if BAN_RE.search(w):
            return False, "적절하지 않은 단어입니다. 다시 입력해 주세요."
    return True, "OK"

# -----------------------------
# 주인공 만들기
# -----------------------------
st.subheader("1) 좋아하는 단어 3개를 적고 주인공을 만들어 보세요 💡")

col1, col2, col3 = st.columns(3)
w1 = col1.text_input("단어 1", max_chars=12)
w2 = col2.text_input("단어 2", max_chars=12)
w3 = col3.text_input("단어 3", max_chars=12)

if st.button("주인공 만들기 👤✨"):
    words = [w1.strip(), w2.strip(), w3.strip()]
    ok, msg = words_valid(words)
    if not ok:
        st.error(msg)
    else:
        prompt = f"""
        초등학교 3학년 어린이들이 읽기 쉬운 문체로,
        '{w1}', '{w2}', '{w3}' 세 단어를 모두 사용해서
        주인공의 이름, 성격, 좋아하는 일, 사는 곳을 소개하는 짧은 설명을 써 주세요.
        예시는 "이름은 루비예요. 밝고 용감한 성격이에요..." 이런 식으로 부탁해요.
        """
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            max_output_tokens=250,
        )
        desc = response.output_text
        st.success("💫 주인공이 완성되었어요!")
        st.write(desc)
        st.session_state["character_desc"] = desc

# -----------------------------
# 8단 이야기 구성
# -----------------------------
st.divider()
st.subheader("2) 주인공의 이야기를 써 볼까요? ✍️")

TITLES = [
    "옛날에", "그리고 매일", "그러던 어느 날",
    "그래서", "그래서", "그래서",
    "마침내", "그날 이후",
]

for i in range(8):
    st.session_state.setdefault(f"story_{i}", "")
    st.session_state.setdefault(f"auto_{i}", False)

for i, title in enumerate(TITLES):
    st.markdown(f"#### {title}")
    if i in [0, 2, 4, 6, 7]:
        st.session_state[f"story_{i}"] = st.text_area(
            f"{title} 내용을 적어보세요",
            value=st.session_state[f"story_{i}"],
            height=80,
            key=f"story_input_{i}",
        )
    else:
        if st.button(f"{title} 자동으로 이어쓰기 🪄", key=f"auto_btn_{i}"):
            prev = st.session_state[f"story_{i-1}"]
            if not prev.strip():
                st.warning("이전 칸의 이야기를 먼저 적어 주세요!")
            else:
                character = st.session_state.get("character_desc", "")
                prompt = f"""
                초등학교 3학년 어린이가 쓴 이야기를 이어서 써 주세요.
                이전 문장은 이렇게 시작해요:
                """{prev}"""
                주인공 정보는 다음과 같아요:
                {character}
                자연스럽게 이어지게 200~300자로 써 주세요.
                너무 어려운 단어는 쓰지 말고, 친근한 문체로 써 주세요.
                """
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=prompt,
                    max_output_tokens=400,
                )
                auto_text = response.output_text.strip()
                st.session_state[f"story_{i}"] = auto_text
                st.session_state[f"auto_{i}"] = True
                st.info("자동으로 이어썼어요 ✨")

        st.text_area(
            f"{title} 자동 생성된 내용",
            value=st.session_state[f"story_{i}"],
            height=120,
            disabled=True,
            key=f"auto_output_{i}",
        )

if st.button("전체 이야기 보기 📖"):
    st.divider()
    st.subheader("📘 완성된 이야기")
    story_text = "\n\n".join(
        [f"**{TITLES[i]}**\n{st.session_state[f'story_{i}']}" for i in range(8)]
    )
    st.write(story_text)
    st.download_button(
        "📥 이야기 저장하기 (txt)",
        data=story_text,
        file_name="my_story.txt",
        mime="text/plain",
    )
