import streamlit as st

main_page = st.Page("main.py", title="Главная"
# , icon=":material/add_circle:"
)
bot_page = st.Page("bot.py", title="Чат-бот"
# , icon=":material/delete:"
)

mbti_page = st.Page("mbti.py", title="MBTI тест"
# , icon=":material/delete:"
)
hh_page = st.Page("hh.py", title="Вакансии"
# , icon=":material/delete:"
)

pg = st.navigation(
    {
            "Main": [main_page, hh_page],
            "Плюшки": [bot_page, mbti_page]
        }
)
st.set_page_config(page_title="Ikanam bot",
                   layout="wide", page_icon="🏆"
# , page_icon=":material/edit:"
)
pg.run()

logo = 'files/beta-1.png'

st.logo(logo, icon_image=logo)