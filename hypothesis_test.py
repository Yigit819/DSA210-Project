import pandas as pd
from scipy import stats
import os

print("=== STATISTICAL HYPOTHESIS TEST: LISTENING DEPTH ===\n")

# --- 1. LOAD THE DATA ---
my_file = 'my_music_taste_profile.csv'
friend_file = 'friend_music_taste_profile.csv'

if not os.path.exists(my_file) or not os.path.exists(friend_file):
    print("Error: Missing CSV files. Make sure you ran main.py for both of you.")
    exit()

my_df = pd.read_csv(my_file)
friend_df = pd.read_csv(friend_file)

# --- 2. SET UP THE HYPOTHESIS ---
print("Question: Do I have a significantly different 'listening depth' (hours per artist) than my friend?")
print("Null Hypothesis (H0): The average hours spent per artist is the same for both of us.")
print("Alternative Hypothesis (H1): There is a significant difference in our average hours per artist.\n")

# Get the array of hours played for both people
my_hours = my_df['hoursPlayed'].dropna()
friend_hours = friend_df['hoursPlayed'].dropna()

print(f"My Average Hours per Artist:     {my_hours.mean():.2f}")
print(f"Friend's Average Hours per Artist: {friend_hours.mean():.2f}\n")

# --- 3. RUN THE INDEPENDENT 2-SAMPLE T-TEST ---
# We use equal_var=False (Welch's T-test) because it's safer if you and your friend 
# have vastly different listening habits or dataset sizes.
t_stat, p_value = stats.ttest_ind(my_hours, friend_hours, equal_var=False)

print(f"T-Statistic: {t_stat:.3f}")
print(f"P-Value:     {p_value:.5e}\n")

# --- 4. INTERPRET THE RESULTS (Alpha = 0.05) ---
if p_value < 0.05:
    print("Conclusion: REJECT the Null Hypothesis.")
    if my_hours.mean() > friend_hours.mean():
        print("Result: You spend significantly MORE time on average per artist than your friend.")
        print("Translation: You are an obsessive listener, they are a casual browser.")
    else:
        print("Result: You spend significantly LESS time on average per artist than your friend.")
        print("Translation: They are an obsessive listener, you are a casual browser.")
else:
    print("Conclusion: FAIL TO REJECT the Null Hypothesis.")
    print("Result: There is no statistically significant difference in how deeply you both listen to artists.")