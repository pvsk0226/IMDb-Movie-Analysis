import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

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

# -----------------------
# 2. Load data
# -----------------------
@st.cache_data(ttl=600)
def load_data():
    query = "SELECT * FROM Movie_details"
    return pd.read_sql(query, engine)

df = load_data()

# -----------------------
# 3. Streamlit UI
# -----------------------
st.set_page_config(page_title="🎬 IMDb 2024 Dashboard", layout="wide")

st.title("IMDb 2024 Dashboard 🎬")

# --- Summary Metrics ---
col1, col2, col3, col4 = st.columns(4)

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

st.markdown("---")  # separator line

# Sidebar filters
st.sidebar.header("Filters")

# Genre filter
genres = df["genre"].dropna().unique()
selected_genres = st.sidebar.multiselect(
    "Select Genre(s):", options=genres, default=genres[:3]
)

# Rating filter
min_rating, max_rating = st.sidebar.slider(
    "Select Rating Range:",
    float(df["rating"].min()),
    float(df["rating"].max()),
    (5.0, 9.0)
)

# Voting filter
min_votes, max_votes = st.sidebar.slider(
    "Select Voting Count Range:",
    int(df["voting_counts"].min(skipna=True)),
    int(df["voting_counts"].max(skipna=True)),
    (0, int(df["voting_counts"].max(skipna=True)))
)

# Duration filter
min_duration, max_duration = st.sidebar.slider(
    "Select Duration Range (in minutes):",
    int(df["duration"].min()),  # Minimum duration
    int(df["duration"].max()),  # Maximum duration
    (90, 180)  # Default range (can be adjusted)
)

# Handle multi-genre filtering
def genre_match(genre_str, selected):
    if pd.isna(genre_str):
        return False
    return any(g in genre_str for g in selected)

# Apply filters
filtered_df = df[df["genre"].apply(lambda g: genre_match(g, selected_genres))]
filtered_df = filtered_df[filtered_df["rating"].between(min_rating, max_rating)]
filtered_df = filtered_df[filtered_df["voting_counts"].between(min_votes, max_votes)]
filtered_df = filtered_df[filtered_df["duration"].between(min_duration, max_duration)]  


# -----------------------
# 4. KPIs
# -----------------------
st.subheader("📌 Key Stats")

col1, col2, col3 = st.columns(3)
col1.metric("Total Movies", len(filtered_df))

# Avg Rating
avg_rating = filtered_df["rating"].mean()
col2.metric("Avg Rating", round(np.nan_to_num(avg_rating, nan=0), 2))

# Avg Votes
avg_votes = filtered_df["voting_counts"].mean()
col3.metric("Avg Votes", int(np.nan_to_num(avg_votes, nan=0)))


# -----------------------
# 5. Charts
# -----------------------
# Top 10 Movies with Highest Ratings and Significant Voting
import altair as alt

st.subheader("🎬 Top 10 Movies (High Rating + Significant Votes)")

# Define a minimum voting threshold
min_vote_threshold = 100  

unique_movies = (
    filtered_df[filtered_df["voting_counts"] >= min_vote_threshold]
    .sort_values(by=["rating", "voting_counts"], ascending=[False, False])
    .drop_duplicates(subset=["movie_name"], keep="first")
)

# Select top 10 movies
top_movies = unique_movies.head(10)

# Display as a table
st.dataframe(top_movies[["movie_name", "genre", "rating", "voting_counts", "duration"]])

# Horizontal bar chart (movie name on y-axis)
chart = (
    alt.Chart(top_movies)
    .mark_bar()
    .encode(
        y=alt.Y("movie_name", sort="-x", title="Movie Name"),
        x=alt.X("rating", title="Rating"),
        tooltip=["movie_name", "genre", "rating", "voting_counts", "duration"],
        color=alt.value("steelblue")
    )
    .properties(width=700, height=400)
)

st.altair_chart(chart, use_container_width=True)

# Average Movie Duration per Genre

st.subheader("⏱️ Average Movie Duration per Genre")

# Group by genre and calculate average duration
avg_duration = (
    filtered_df.groupby("genre")["duration"]
    .mean()
    .sort_values(ascending=True)   # sort for better readability
)


# Or for more control using matplotlib
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 4))
avg_duration.plot(kind="barh", ax=ax, color="orange")
ax.set_xlabel("Average Duration (minutes)")
ax.set_ylabel("Genre")
ax.set_title("Average Movie Duration per Genre")

# Show average value at the end of each bar
for i, v in enumerate(avg_duration):
    ax.text(v + 2, i, f"{v:.1f}", va="center")

st.pyplot(fig)


# Genre distribution (Horizontal Bar Chart with Labels)
st.subheader("🎭 Genre Distribution")

genre_counts = filtered_df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig1 = px.bar(
    genre_counts,
    x="count",
    y="genre",
    orientation="h",   # horizontal
    text="count",      # show movie count
    labels={"genre": "Genre", "count": "Number of Movies"},
    title="Movies by Genre"
)

# Set text position to appear outside the bars
fig1.update_traces(textposition="outside")

st.plotly_chart(fig1, use_container_width=True)

# Voting Trends by Genre
st.subheader("🗳️ Voting Trends by Genre")

# Calculate average votes per genre
avg_votes_by_genre = (
    filtered_df.groupby("genre")["voting_counts"]
    .mean()
    .reset_index()
    .sort_values(by="voting_counts", ascending=False)
)

# Plot horizontal bar chart
fig2 = px.bar(
    avg_votes_by_genre,
    x="voting_counts",
    y="genre",
    orientation="h",
    text=avg_votes_by_genre["voting_counts"].round(0),  # show rounded avg votes
    labels={"voting_counts": "Average Votes", "genre": "Genre"},
    title="Average Voting Counts by Genre"
)

# Position text outside bars
fig2.update_traces(textposition="outside")

st.plotly_chart(fig2, use_container_width=True)

#Rating Distogram
st.subheader("⭐ Rating Distribution")

# Histogram of ratings
fig_hist = px.histogram(
    filtered_df,
    x="rating",
    nbins=20,  # adjust number of bins
    title="Histogram of Movie Ratings",
    labels={"rating": "Rating"},
    marginal="box"  # adds a small boxplot above histogram
)

st.plotly_chart(fig_hist, use_container_width=True)

fig_box = px.box(
    filtered_df,
    y="rating",
    title="Boxplot of Movie Ratings",
    labels={"rating": "Rating"}
)

st.plotly_chart(fig_box, use_container_width=True)  

st.subheader("🏆 Genre-Based Rating Leaders")

# Step 1: Sort by rating (and votes as tie-breaker)
genre_leaders = (
    df.sort_values(["genre", "rating", "voting_counts"], ascending=[True, False, False])
      .groupby("genre")
      .first()
      .reset_index()
)

# Step 2: Show table
st.dataframe(
    genre_leaders[["genre", "movie_name", "rating", "voting_counts", "duration"]],
    use_container_width=True
)



# Group genres by total votes
genre_votes = (
    df.groupby("genre")["voting_counts"].sum().reset_index()
    .sort_values(by="voting_counts", ascending=False)
)

st.subheader("🥇 Most Popular Genres by Voting")

# Group by genre total votes
genre_votes = (
    df.groupby("genre")["voting_counts"].sum().reset_index()
    .sort_values(by="voting_counts", ascending=False)
)

# Take top 8 genres, rest as 'Others'
top_n = 6
top_genres = genre_votes.head(top_n)
others = pd.DataFrame({
    "genre": ["Others"],
    "voting_counts": [genre_votes["voting_counts"].iloc[top_n:].sum()]
})
genre_votes_clean = pd.concat([top_genres, others])

# Pie chart
fig = px.pie(
    genre_votes_clean,
    names="genre",
    values="voting_counts",
    title="Most Popular Genres by Voting",
    hole=0.4
)

# Remove decimals and show labels clearly
fig.update_traces(
    textinfo="label+percent",
    texttemplate="%{label}: %{percent:.0%}"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("⏳ Shortest and Longest movies")

# Get 5 shortest and 5 longest
shortest_5 = df.nsmallest(5, "duration")[["movie_name", "genre", "duration"]]
longest_5 = df.nlargest(5, "duration")[["movie_name", "genre", "duration"]]

# Display side by side
col1, col2 = st.columns(2)

with col1:
    st.markdown("**📌 Shortest Movies**")
    st.table(shortest_5.reset_index(drop=True))

with col2:
    st.markdown("**📌 Longest Movies**")
    st.table(longest_5.reset_index(drop=True))

# Heatmap comparison of average rating across genres

import plotly.express as px

st.subheader("🔥 Ratings by Genre (Heatmap)")

# Group by genre and calculate avg rating
ratings_by_genre = (
    df.groupby("genre")["rating"]
    .mean()
    .reset_index()
    .sort_values(by="rating", ascending=False)
)

# Create heatmap
fig = px.imshow(
    [ratings_by_genre["rating"]],
    labels=dict(x="Genre", color="Avg Rating"),
    x=ratings_by_genre["genre"],
    y=["Average Rating"],
    color_continuous_scale="Blues",
)

fig.update_layout(
    xaxis=dict(tickangle=45),
    yaxis=dict(showticklabels=True),
    title="Average Ratings by Genre"
)

st.plotly_chart(fig, use_container_width=True)

# Correlation
# --- Correlation Analysis: Ratings vs Voting Counts ---

st.subheader("Correlation Between Ratings and Voting Counts")
 # Remove rows with NaN values in the key columns
filtered_df = filtered_df.dropna(subset=["rating", "voting_counts"])

    
# Ensure the columns are of type float
filtered_df["rating"] = filtered_df["rating"].astype(float)
filtered_df["voting_counts"] = filtered_df["voting_counts"].astype(float)

    # Check the structure of the DataFrame
st.write(filtered_df.head())

    # Create the scatter plot
try:
        fig = px.scatter(
            filtered_df, 
            x="voting_counts",  # Use the correct column name 'voting_counts'
            y="rating",  # Use the correct column name 'rating'
            color="genre", 
            hover_data=["movie_name"],  # Use the correct column name 'movie_name'
            title="Correlation Between Ratings and Voting Counts"
        )
        st.plotly_chart(fig)

        # Calculate and display correlation coefficient
        correlation = filtered_df["rating"].corr(filtered_df["voting_counts"])
        st.write(f"Correlation coefficient between Rating and Voting Counts: {correlation:.2f}")

except Exception as e:
        st.error(f"An error occurred: {e}")









