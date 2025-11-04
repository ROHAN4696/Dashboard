import streamlit as st
df = st.session_state['netflix_df']

st.title("Director search")

directors = df['director'].dropna().unique()
directors = sorted(directors)

selected_director = st.selectbox("Select a Director", directors)

filtered_df = df[df['director'] == selected_director]

st.subheader(f"Movies/Shows directed by {selected_director}")
st.dataframe(filtered_df[['title', 'type', 'release_year', 'country', 'listed_in']])

st.title("Cast search")

actors = (
    df['cast']
    .dropna()
    .apply(lambda x: [a.strip() for a in x.split(',')])
    .explode()
    .unique()
)

cast = sorted(actors)

selected_cast = st.selectbox("Select a Cast", cast)

filtered_cast_df = df[df['cast'].fillna("").str.contains(selected_cast, case=False)]

st.subheader(f"Movies/Shows which casted {selected_cast}")
st.dataframe(filtered_cast_df[['title', 'type', 'release_year', 'country', 'listed_in']])