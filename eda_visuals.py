import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --- 1. DATA PROCESSING FOR GENRES ---
def process_genre_data(file_path):
    """Loads the taste profile, explodes comma-separated genres, and calculates hours per genre."""
    if not os.path.exists(file_path):
        print(f"Warning: Could not find {file_path}. Make sure you ran main.py for this person.")
        return pd.DataFrame() 

    df = pd.read_csv(file_path)
    
    # Drop rows where tags/genres are missing
    df = df.dropna(subset=['tags'])
    
    # Split the comma-separated tags into an actual Python list
    df['tags'] = df['tags'].apply(lambda x: [tag.strip() for tag in str(x).split(',')])
    
    # 'Explode' the lists so each tag gets its own row, carrying the artist's hours played with it
    exploded_df = df.explode('tags')
    
    # Group by the specific genre and sum the total hours played across all artists in that genre
    genre_stats = exploded_df.groupby('tags')['hoursPlayed'].sum().reset_index()
    genre_stats = genre_stats.sort_values(by='hoursPlayed', ascending=False)
    genre_stats.rename(columns={'tags': 'genre'}, inplace=True)
    
    return genre_stats

# --- 2. BASIC EDA: TOP GENRES BAR CHART ---
def plot_top_genres(genre_df, title="My Top 10 Genres", filename='my_top_genres.png'):
    plt.figure(figsize=(10, 6))
    
    # A bar chart is the best way to visualize categorical data like genres
    sns.barplot(data=genre_df.head(10), x='hoursPlayed', y='genre', hue='genre', palette='viridis', legend=False)    
    plt.title(title, fontsize=16)
    plt.xlabel('Hours Played')
    plt.ylabel('Genre')
    plt.tight_layout()
    
    plt.savefig(filename)
    print(f"Saved '{filename}'")
    plt.close()

# --- 3. TASTE COMPARISON USING COSINE SIMILARITY ---
# --- 3. TASTE COMPARISON USING PROPORTIONAL OVERLAP ---
def compare_tastes(my_genres, friend_genres, friend_name="My Friend"):
    if friend_genres.empty:
        print("Skipping comparison because friend data is missing.")
        return

    # Merge the two genre lists together into one dataframe
    merged_df = pd.merge(my_genres, friend_genres, on='genre', how='outer', suffixes=('_me', '_friend'))
    
    # Fill missing values with 0 
    merged_df = merged_df.fillna(0)
    
    # --- NEW MATH: RELATIVE FREQUENCIES (SUMMARY STATISTICS) ---
    # 1. Convert raw hours into proportions (percentages of total listening time)
    total_hours_me = merged_df['hoursPlayed_me'].sum()
    total_hours_friend = merged_df['hoursPlayed_friend'].sum()
    
    merged_df['prop_me'] = merged_df['hoursPlayed_me'] / total_hours_me
    merged_df['prop_friend'] = merged_df['hoursPlayed_friend'] / total_hours_friend
    
    # 2. Find the intersection (overlap) for each genre
    # If you listen to 40% rap and they listen to 15% rap, the shared overlap is 15%
    merged_df['shared_proportion'] = merged_df[['prop_me', 'prop_friend']].min(axis=1)
    
    # 3. Sum all the overlaps to get your final Match Percentage
    match_percentage = round(merged_df['shared_proportion'].sum() * 100, 1)
    
    print(f"\nTaste Match with {friend_name}: {match_percentage}%")
    
    # 3b. Plot the Top Shared Genres
    # A shared genre is one where both of you have > 0 hours
    shared_df = merged_df[(merged_df['hoursPlayed_me'] > 0) & (merged_df['hoursPlayed_friend'] > 0)].copy()
    
    # Calculate a combined score to find the most heavily shared genres
    shared_df['combined_hours'] = shared_df['hoursPlayed_me'] + shared_df['hoursPlayed_friend']
    top_shared = shared_df.sort_values(by='combined_hours', ascending=False).head(10)
    
    # 'Melt' the dataframe to make it easy to plot side-by-side bars in Seaborn
    plot_df = top_shared.melt(id_vars='genre', value_vars=['hoursPlayed_me', 'hoursPlayed_friend'], 
                              var_name='Person', value_name='Hours')
    plot_df['Person'] = plot_df['Person'].replace({'hoursPlayed_me': 'Me', 'hoursPlayed_friend': friend_name})
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=plot_df, x='Hours', y='genre', hue='Person', palette='Set2')
    
    plt.title(f"Top Shared Genres (Taste Overlap: {match_percentage}%)", fontsize=16)
    plt.xlabel('Hours Played')
    plt.ylabel('Genre')
    plt.tight_layout()
    
    plt.savefig('taste_comparison_bar.png')
    print("Saved 'taste_comparison_bar.png'")
    plt.close()
    
# --- 4. RUN THE VISUALIZATIONS ---
print("Loading genre profiles...\n")

# Load your personal data
my_genre_data = process_genre_data('my_music_taste_profile.csv')

if not my_genre_data.empty:
    # 1. Generate your personal EDA plot
    plot_top_genres(my_genre_data, title="My Top 10 Genres", filename="my_top_genres.png")
    
    # 2. Compare with a friend!
    # IMPORTANT: You need to run main.py using your friend's Spotify JSONs first, 
    # and save the output as 'friend_music_taste_profile.csv'
    print("\nLoading friend's profile for comparison...")
    friend_genre_data = process_genre_data('friend_music_taste_profile.csv')
    
    compare_tastes(my_genre_data, friend_genre_data, friend_name="My Friend")