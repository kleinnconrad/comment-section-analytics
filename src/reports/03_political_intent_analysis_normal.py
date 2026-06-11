import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.config.political_config import CURRENT_LEXICON, POLITICAL_MAJORITY_THRESHOLD
import re

def classify_text_intent(text):
    if not isinstance(text, str):
        return 'neutral'
    text = str(text).lower()
    
    # Use regex to find words inside strings
    left_score = sum(1 for word in CURRENT_LEXICON['left_wing'] if re.search(r'\b' + re.escape(word) + r'\b', text))
    right_score = sum(1 for word in CURRENT_LEXICON['right_wing'] if re.search(r'\b' + re.escape(word) + r'\b', text))
    
    # We only count if there is a STRICT difference
    if left_score > 0 and left_score > right_score:
        return 'left'
    elif right_score > 0 and right_score > left_score:
        return 'right'
    return 'neutral'

def run():
    print("Loading databases for political intent analysis (NORMAL USERS)...")
    conn = sqlite3.connect('db/corpus.sqlite3')
    preds = pd.read_csv('data/prof_writing_analytics/predictions.csv')
    
    if 'y_pred_any' not in preds.columns:
        preds['y_pred_any'] = preds[['is_professional_temporal', 'is_professional_topic', 'is_professional_content', 'is_professional_impact']].max(axis=1)

    print("Fetching raw posts for NON professional writers...")
    preds.rename(columns={'user_id': 'ID_User'}, inplace=True)
    # INVERTED CONDITION: y_pred_any == 0
    flagged_posts = preds[preds['y_pred_any'] == 0].copy()
    
    print(f"Classifying intent for {len(flagged_posts):,} normal comments. This will take a moment...")
    # The 'comment' column in predictions.csv contains the actual text!
    flagged_posts['Intent'] = flagged_posts['comment'].apply(classify_text_intent)
    
    print("Aggregating intent per normal user...")
    # Debug print the total classified
    print(f"Total normal posts with 'left' intent: {(flagged_posts['Intent'] == 'left').sum()}")
    print(f"Total normal posts with 'right' intent: {(flagged_posts['Intent'] == 'right').sum()}")
    
    # We only care about left/right for the ratio
    pol_posts = flagged_posts[flagged_posts['Intent'].isin(['left', 'right'])]
    
    user_intent = pol_posts.groupby(['ID_User', 'Intent']).size().unstack(fill_value=0)
    if 'left' not in user_intent.columns: user_intent['left'] = 0
    if 'right' not in user_intent.columns: user_intent['right'] = 0
    
    user_intent['total_pol'] = user_intent['left'] + user_intent['right']
    user_intent['left_ratio'] = user_intent['left'] / user_intent['total_pol']
    user_intent['right_ratio'] = user_intent['right'] / user_intent['total_pol']
    
    # Apply 80% majority rule
    user_intent['Assigned_Spectrum'] = 'neutral'
    user_intent.loc[user_intent['left_ratio'] >= POLITICAL_MAJORITY_THRESHOLD, 'Assigned_Spectrum'] = 'Left Wing'
    user_intent.loc[user_intent['right_ratio'] >= POLITICAL_MAJORITY_THRESHOLD, 'Assigned_Spectrum'] = 'Right Wing'
    user_intent.loc[user_intent['total_pol'] == 0, 'Assigned_Spectrum'] = 'neutral' # Safety check
    
    final_spectrum = user_intent[user_intent['Assigned_Spectrum'] != 'neutral'].reset_index()
    
    print(f"Successfully classified {len(final_spectrum)} NORMAL writers into strict Left/Right spectrums based on >= {POLITICAL_MAJORITY_THRESHOLD*100}% majority.")
    
    # Map back to detailed paths
    print("Mapping to detailed paths to see what they target...")
    articles = pd.read_sql('SELECT ID_Article as article, Path FROM Articles', conn)
    # Get all posts made by these strict political users
    strict_users = final_spectrum[['ID_User', 'Assigned_Spectrum']]
    strict_posts = pd.merge(flagged_posts, strict_users, on='ID_User', how='inner')
    
    # Merge with article paths
    final_df = pd.merge(strict_posts, articles, on='article', how='left')
    
    # Extract year
    final_df['timestamp'] = pd.to_datetime(final_df['timestamp'])
    final_df['Year'] = final_df['timestamp'].dt.year

    print("Generating Political Spectrum Target Chart (TOTAL - NORMAL)...")
    top_paths = final_df['Path'].value_counts().head(15).index
    plot_data = final_df[final_df['Path'].isin(top_paths)]
    
    plt.figure(figsize=(14, 8))
    sns.countplot(data=plot_data, y='Path', hue='Assigned_Spectrum', order=top_paths, palette={'Left Wing': '#E41A1C', 'Right Wing': '#377EB8'})
    plt.title(f'Targets of Highly Partisan NORMAL Writers (TOTAL)\n(Users with >{int(POLITICAL_MAJORITY_THRESHOLD*100)}% Ideological Consistency)', fontsize=14, pad=15)
    plt.xlabel('Number of Normal Comments')
    plt.ylabel('Detailed Newspaper Path')
    plt.legend(title='Assigned Political Spectrum')
    plt.tight_layout()
    plt.savefig('results/prof_writing_analytics/political_spectrum_targets_normal_total.png', dpi=300)
    plt.close()

    print("Generating charts by Year...")
    years = [2015, 2016]
    
    md_content = f"# Political Spectrum Targets By Year (NORMAL USERS)\n\nTotal Users Classified: **{len(final_spectrum):,}**\n\n## Total Dataset\n![Total](./political_spectrum_targets_normal_total.png)\n\n"
    
    for year in years:
        year = int(year)
        print(f"Generating chart for {year}...")
        year_df = final_df[final_df['Year'] == year]
        year_top_paths = year_df['Path'].value_counts().head(15).index
        
        if len(year_top_paths) == 0:
            continue
            
        plot_data_year = year_df[year_df['Path'].isin(year_top_paths)]
        
        plt.figure(figsize=(14, 8))
        sns.countplot(data=plot_data_year, y='Path', hue='Assigned_Spectrum', order=year_top_paths, palette={'Left Wing': '#E41A1C', 'Right Wing': '#377EB8'})
        plt.title(f'Targets of Highly Partisan NORMAL Writers ({year})\n(Users with >{int(POLITICAL_MAJORITY_THRESHOLD*100)}% Ideological Consistency)', fontsize=14, pad=15)
        plt.xlabel('Number of Normal Comments')
        plt.ylabel('Detailed Newspaper Path')
        plt.legend(title='Assigned Political Spectrum')
        plt.tight_layout()
        plt.savefig(f'results/prof_writing_analytics/political_spectrum_targets_normal_{year}.png', dpi=300)
        plt.close()
        
        md_content += f"## {year}\n![{year}](./political_spectrum_targets_normal_{year}.png)\n\n"

    print("Writing chronological report...")
    with open('results/prof_writing_analytics/political_timeline_normal.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print("Normal users political intent analysis complete!")

if __name__ == '__main__':
    run()
