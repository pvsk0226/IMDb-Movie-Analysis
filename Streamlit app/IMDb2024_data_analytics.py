import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import altair as alt

# -----------------------
# 1. Database connection
# -----------------------
user = "3LBRyXkYRgoP1FS.root"
password = "fwJACxECJe0b7ZlM"
host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
port = 4000
database = "imdb2024A"

connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?ssl_ca=C:/Users/pavit/ca.pem"
engine = create_engine(connection_string)

# ---------------------
# Load Data
# ---------------------
@st.cache_data(ttl=600)
def load_data():
    query = "SELECT * FROM Movie_details"
    return pd.read_sql(query, engine)

df = load_data()

#3. Streamlit UI
# -----------------------
st.set_page_config(page_title="IMDb 2024 Analytics", layout="wide")
st.title("🎬 IMDb 2024 Analytics Dashboard")

# Clean duplicates if needed
df = df.drop_duplicates(subset="movie_name")


# --- Summary Metrics ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Movies", df.shape[0])

with col2:
    top_rated = df.loc[df['rating'].idxmax()]
    st.metric("Highest Rated", f"{top_rated['movie_name']}", f"{top_rated['rating']}⭐")

with col3:
    top_voted = df.loc[df['voting_counts'].idxmax()]
    st.metric("Most Voted", f"{top_voted['movie_name']}", f"{top_voted['voting_counts']} votes")

with col4:
    longest = df.loc[df['duration'].idxmax()]
    st.metric("Longest Movie", f"{longest['movie_name']}", f"{longest['duration']} mins")

with col5:
    shortest = df.loc[df['duration'].idxmin()]
    st.metric("Shortest Movie", f"{shortest['movie_name']}", f"{shortest['duration']} mins")

st.markdown("---")  # separator line


# ---------------------
# 2. Top 10 Movies
# ---------------------
st.subheader("🏆 Top 10 Movies (High Rating + Significant Votes)")
min_vote_threshold = 100

top_movies = (
    df[df["voting_counts"] >= min_vote_threshold]
    .sort_values(by=["rating", "voting_counts"], ascending=[False, False])
    .drop_duplicates(subset="movie_name")
    .head(10)
)

st.dataframe(top_movies[["movie_name", "genre", "rating", "voting_counts", "duration"]])

chart = (
    alt.Chart(top_movies)
    .mark_bar()
    .encode(
        y=alt.Y("movie_name:N", sort="-x", title="Movie"),
        x=alt.X("rating:Q", title="Rating"),
        color=alt.value("steelblue")
    )
)
st.altair_chart(chart, use_container_width=True)

# ---------------------
# 3. Genre Distribution
# ---------------------
st.subheader("🎭 Genre Distribution")
genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = px.bar(
    genre_counts,
    x="genre",
    y="count",
    text="count",
    title="Movies by Genre"
)
fig1.update_traces(textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

# ---------------------
# 4. Voting Trends by Genre
# ---------------------
st.subheader("📊 Voting Trends by Genre")
avg_votes = df.groupby("genre")["voting_counts"].mean().reset_index()

fig2 = px.bar(
    avg_votes,
    x="genre",
    y="voting_counts",
    text="voting_counts",
    title="Average Votes by Genre"
)
fig2.update_traces(texttemplate='%{text:.0f}', textposition="outside")
st.plotly_chart(fig2, use_container_width=True)

# ---------------------
# 5. Rating Distribution
# ---------------------
st.subheader("⭐ Rating Distribution")
fig3, ax = plt.subplots()
sns.histplot(df["rating"], bins=20, kde=True, ax=ax)
st.pyplot(fig3)

# ---------------------
# 6. Genre-Based Rating Leaders
# ---------------------
st.subheader("🥇 Genre-Based Rating Leaders")
top_by_genre = df.loc[df.groupby("genre")["rating"].idxmax()]
st.dataframe(top_by_genre[["genre", "movie_name", "rating", "voting_counts"]])

# ---------------------
# 7. Most Popular Genres by Voting
# ---------------------
st.subheader("🔥 Most Popular Genres by Voting")
genre_votes = df.groupby("genre")["voting_counts"].sum().reset_index()
fig4 = px.pie(genre_votes, names="genre", values="voting_counts", title="Genres by Total Votes")
st.plotly_chart(fig4, use_container_width=True)

# ---------------------
# 8. Duration Insights
# ---------------------
st.subheader("⏳ Average Duration per Genre")
avg_duration = df.groupby("genre")["duration"].mean().reset_index()

fig5 = px.bar(
    avg_duration,
    x="duration",
    y="genre",
    orientation="h",
    text="duration",
    title="Average Duration by Genre"
)
fig5.update_traces(texttemplate='%{text:.0f} min', textposition="outside")
st.plotly_chart(fig5, use_container_width=True)

# ---------------------
# 9. Duration Extremes
# ---------------------
st.subheader("🎬 Duration Extremes (Top 5 Shortest & Longest)")
shortest5 = df.nsmallest(5, "duration")[["movie_name", "duration"]]
longest5 = df.nlargest(5, "duration")[["movie_name", "duration"]]

col6, col7 = st.columns(2)
with col6:
    st.write("📏 Shortest Movies")
    st.dataframe(shortest5)
with col7:
    st.write("📐 Longest Movies")
    st.dataframe(longest5)

# ---------------------
# 10. Ratings by Genre (Heatmap)
# ---------------------
st.subheader("🎨 Ratings by Genre (Heatmap)")
avg_ratings = df.groupby("genre")["rating"].mean().reset_index()

fig6, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(
    avg_ratings.pivot_table(values="rating", index="genre", aggfunc="mean"),
    annot=True, cmap="Blues", cbar=False
)
st.pyplot(fig6)

# Correlation Analysis: Ratings vs Voting Counts
st.subheader("📊 Correlation Analysis: Ratings vs Voting Counts")

fig_corr = px.scatter(
    df,
    x="rating",
    y="voting_counts",
    hover_data=["movie_name", "genre"],
    title="Relationship between Ratings and Voting Counts",
    labels={"rating": "Movie Rating", "voting_counts": "Voting Counts"},
    opacity=0.6,
    color="genre"
)

st.plotly_chart(fig_corr, use_container_width=True)

