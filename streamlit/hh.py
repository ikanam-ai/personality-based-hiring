import streamlit as st
import pandas as pd

df = pd.read_csv('files/hh_dataset.csv') 

df['salary_range'] = (df['salary_to'] + df['salary_from'])//2

st.title("Подбор наиболее подходящих вакансий по MBTI")
st.subheader("`Параметры поиска`")
user_mbti = st.selectbox("Ваш MBTI", df['mbti'].unique())
user_experience = st.selectbox("Опыт работы", df['experience'].unique())
user_schedule = st.selectbox("График работы", df['schedule_label'].unique())
user_salary = st.number_input("Желаемая зарплата", min_value=0, step=10000)

filtered_df = df[df['mbti'] == user_mbti]

filtered_df = filtered_df[(filtered_df['experience'] == user_experience) &
                          (filtered_df['schedule_label'] == user_schedule)]

filtered_df['salary_difference'] = abs(filtered_df['salary_range'] - user_salary)
filtered_df = filtered_df.sort_values(by='salary_difference').head(3)


st.write("#### `Результаты поиска:`")
columns = st.columns(3)  

for i, (index, row) in enumerate(filtered_df.iterrows()):
    with columns[i]:  
        skills_to_show = ", ".join(row['skills'].split(", ")[:5]) 
        st.write("### Вакансия:", row['name'])
        st.write("**Компания:**", row['employer_name'])
        st.write("**Зарплата:** от", row['salary_from'], "до", row['salary_to'], row['salary_currency'])
        st.write("**Опыт работы:**", row['experience'])
        st.write("**График работы:**", row['schedule_label'])
        st.write("**Навыки:**", skills_to_show)
        st.write("---")