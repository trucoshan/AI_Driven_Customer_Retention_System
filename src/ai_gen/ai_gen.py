from groq import Groq
import streamlit as st

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

def generate_churn_explanation(
    probability,
    good_signs,
    bad_signs
):

    with open(
        "src/ai_gen/prompt.txt",
        "r",
        encoding="utf-8"
    ) as file:
        
        prompt_temp = file.read()

    prompt = prompt_temp.format(
        probability=probability,
        good_signs=good_signs,
        bad_signs=bad_signs,
    )

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content":
                "You are a telecom churn analyst."
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.5

    )

    return response.choices[0].message.content