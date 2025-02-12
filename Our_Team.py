import streamlit as st

def app():
    st.title("Meet Our Team")

    # Team Members Data
    team_members = [
        {"name": "Bibin", "role": "", "img": "./static/bibin.jpg"},
        {"name": "Chetan", "role": "", "img": "./static/Chetan.jpg"},
        {"name": "Mukund", "role": "", "img": "./static/Image.jpg"},
        {"name": "Manisha", "role": "", "img": "./static/Manisha.jpg"},
    ]

    cols = st.columns(len(team_members))

    for col, member in zip(cols, team_members):
        with col:
            st.image(member["img"], width=150, caption=member["name"])

if __name__ == "__main__":
    app()
