import pandas as pd
import json
import requests
import time
import os

# --- 1. CONFIGURATION ---
LASTFM_API_KEY = '9703ff436b8d1bd883dca296746c5b98' 
LASTFM_URL = 'http://ws.audioscrobbler.com/2.0/'

# --- 2. LOAD AND CLEAN THE DATA ---
file_names = ['StreamingHistory_music_0.json', 'StreamingHistory_music_1.json', 'StreamingHistory_music_2.json']
all_data = []

print("Loading Spotify data...")
for file_name in file_names:
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as file:
            all_data.extend(json.load(file))

df = pd.DataFrame(all_data)

# Filter out skips (less than 30 seconds)
filtered_df = df[df['msPlayed'] >= 30000].copy()

# --- 3. AGGREGATE BY ARTIST ---
# We calculate total listening time per artist to figure out your top genres later
artist_stats = filtered_df.groupby('artistName')['msPlayed'].sum().reset_index()
unique_artists = artist_stats['artistName'].tolist()

# --- 4. FETCH GENRES FROM LAST.FM ---
progress_file = 'artist_genres.csv'

# Load existing progress if it exists
if os.path.exists(progress_file):
    saved_genres_df = pd.read_csv(progress_file)
    processed_artists = saved_genres_df['artistName'].tolist()
    print(f"Found saved progress! Skipping {len(processed_artists)} already fetched artists...")
else:
    processed_artists = []
    print(f"Total unique artists to search for: {len(unique_artists)}")

artists_to_fetch = [a for a in unique_artists if a not in processed_artists]

for index, artist in enumerate(artists_to_fetch):
    try:
        # Prepare the Last.fm API request
        params = {
            'method': 'artist.gettoptags',
            'artist': artist,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
            'autocorrect': 1
        }
        
        response = requests.get(LASTFM_URL, params=params)
        data = response.json()
        
        genres = []
        if 'toptags' in data and 'tag' in data['toptags']:
            # Grab the top 3 tags, ignoring empty ones
            tags = data['toptags']['tag']
            genres = [tag['name'].lower() for tag in tags[:3]]
        
        # Convert list of genres to a comma-separated string
        genre_string = ", ".join(genres) if genres else "unknown"
        
        # Save immediately to CSV
        pd.DataFrame({'artistName': [artist], 'genres': [genre_string]}).to_csv(
            progress_file, mode='a', header=not os.path.exists(progress_file), index=False
        )
        
        if (index + 1) % 50 == 0:
            print(f"Fetched genres for {index + 1} artists...")
            
        time.sleep(0.25)
        
    except Exception as e:
        print(f"Error fetching {artist}: {e}")
        time.sleep(1) # Back off a bit if there's an error

print("\nFinished fetching genres!")

# --- 5. MERGE AND EXPORT ---
if os.path.exists(progress_file):
    genres_df = pd.read_csv(progress_file)
    final_df = pd.merge(artist_stats, genres_df, on='artistName', how='left')
    
    # Convert msPlayed to hours for easier reading
    final_df['hoursPlayed'] = final_df['msPlayed'] / (1000 * 60 * 60)
    final_df = final_df.sort_values(by='hoursPlayed', ascending=False)
    
    final_df.to_csv('my_music_taste_profile.csv', index=False)
    print("\nSuccess! Saved your complete profile to 'my_music_taste_profile.csv'")
    print(final_df[['artistName', 'genres', 'hoursPlayed']].head(10)) 
