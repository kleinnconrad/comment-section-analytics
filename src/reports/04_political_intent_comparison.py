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
    """
    Classify the political intent of a given text as left, right, or neutral.
    
    Args:
        text (str): The input text to classify.
        
    Returns:
        str: The classified intent.
    """
    if not isinstance(text, str):
        return 'neutral'
    text = str(text).lower()
    
    left_score = sum(1 for word in CURRENT_LEXICON['left_wing'] if re.search(r'\b' + re.escape(word) + r'\b', text))
    right_score = sum(1 for word in CURRENT_LEXICON['right_wing'] if re.search(r'\b' + re.escape(word) + r'\b', text))
    
    if left_score > 0 and left_score > right_score:
        return 'left'
    elif right_score > 0 and right_score > left_score:
        return 'right'
    return 'neutral'

def run():
    """
    Run the unified political intent comparison between astroturfers and normal users.
    """
    print("Loading databases for unified political intent comparison...")
    conn = sqlite3.connect('db/corpus.sqlite3')
    preds = pd.read_csv('data/prof_writing_analytics/predictions.csv')
    
    if 'y_pred_any' not in preds.columns:
        preds['y_pred_any'] = preds[['is_professional_temporal', 'is_professional_topic', 'is_professional_content', 'is_professional_impact']].max(axis=1)

    preds.rename(columns={'user_id': 'ID_User'}, inplace=True)
    
    # We will classify the entire 1M dataset to generate the comparison
    print(f"Classifying intent for {len(preds):,} total comments. This will take ~7-8 minutes...")
    preds['Intent'] = preds['comment'].apply(classify_text_intent)
    
    print("Aggregating intent per user...")
    pol_posts = preds[preds['Intent'].isin(['left', 'right'])]
    
    # Group by User to find ideological consistency
    user_intent = pol_posts.groupby(['ID_User', 'Intent']).size().unstack(fill_value=0)
    if 'left' not in user_intent.columns:
        user_intent['left'] = 0
    if 'right' not in user_intent.columns:
        user_intent['right'] = 0
    
    user_intent['total_pol'] = user_intent['left'] + user_intent['right']
    user_intent['left_ratio'] = user_intent['left'] / user_intent['total_pol']
    user_intent['right_ratio'] = user_intent['right'] / user_intent['total_pol']
    
    # Apply 80% majority rule
    user_intent['Assigned_Spectrum'] = 'neutral'
    user_intent.loc[user_intent['left_ratio'] >= POLITICAL_MAJORITY_THRESHOLD, 'Assigned_Spectrum'] = 'Left Wing'
    user_intent.loc[user_intent['right_ratio'] >= POLITICAL_MAJORITY_THRESHOLD, 'Assigned_Spectrum'] = 'Right Wing'
    user_intent.loc[user_intent['total_pol'] == 0, 'Assigned_Spectrum'] = 'neutral'
    
    # Filter only partisan users
    partisan_users = user_intent[user_intent['Assigned_Spectrum'] != 'neutral'].reset_index()
    partisan_users = partisan_users[['ID_User', 'Assigned_Spectrum']]
    
    # Merge back to get whether they are professional or normal
    user_types = preds.drop_duplicates(subset=['ID_User'])[['ID_User', 'y_pred_any']]
    partisan_users = pd.merge(partisan_users, user_types, on='ID_User', how='inner')
    partisan_users['Writer_Type'] = partisan_users['y_pred_any'].map({1: 'Professional Astroturfer', 0: 'Normal User'})
    
    print(f"Total Partisan Users: {len(partisan_users)}")
    
    # --- REPORT 1: Share of Left vs Right Grouped by Professional/Normal ---
    print("Generating Ideological Share Comparison Chart...")
    
    # Calculate percentage shares
    spectrum_counts = partisan_users.groupby(['Writer_Type', 'Assigned_Spectrum']).size().reset_index(name='Count')
    total_by_type = spectrum_counts.groupby('Writer_Type')['Count'].transform('sum')
    spectrum_counts['Share (%)'] = (spectrum_counts['Count'] / total_by_type) * 100

    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=spectrum_counts, x='Writer_Type', y='Share (%)', hue='Assigned_Spectrum', palette={'Left Wing': '#E41A1C', 'Right Wing': '#377EB8'})
    plt.title(f'Ideological Distribution of Highly Partisan Commenters\n(Users with >{int(POLITICAL_MAJORITY_THRESHOLD*100)}% Consistency)', fontsize=15, pad=20)
    plt.ylabel('Percentage of Users within Group')
    plt.xlabel('')
    
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.1f}%', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=12, color='black', xytext=(0, 5), 
                        textcoords='offset points')

    plt.tight_layout()
    plt.savefig('results/prof_writing_analytics/ideological_share_comparison.png', dpi=300)
    plt.close()
    
    # --- REPORT 2: Same but grouped by Detailed Path ---
    print("Generating Share Comparison Grouped by Detailed Path...")
    articles = pd.read_sql('SELECT ID_Article as article, Path FROM Articles', conn)
    
    # Get all posts from these partisan users
    partisan_posts = pd.merge(preds, partisan_users, on='ID_User', how='inner')
    partisan_posts = pd.merge(partisan_posts, articles, on='article', how='left')
    
    # We want the top 10 most targeted paths overall
    top_paths = partisan_posts['Path'].value_counts().head(10).index
    path_data = partisan_posts[partisan_posts['Path'].isin(top_paths)]
    
    # Group by Path, Writer_Type, and Spectrum to count POSTS
    path_counts = path_data.groupby(['Path', 'Writer_Type', 'Assigned_Spectrum']).size().reset_index(name='Count')
    total_by_path_type = path_counts.groupby(['Path', 'Writer_Type'])['Count'].transform('sum')
    path_counts['Share (%)'] = (path_counts['Count'] / total_by_path_type) * 100
    path_counts.fillna(0, inplace=True)
    
    # Plot using a seaborn categorical factorplot (catplot)
    g = sns.catplot(
        data=path_counts, kind='bar',
        x='Share (%)', y='Path', hue='Assigned_Spectrum', col='Writer_Type',
        palette={'Left Wing': '#E41A1C', 'Right Wing': '#377EB8'},
        height=7, aspect=1.2, sharex=True
    )
    g.fig.suptitle(f'Ideological Share of Comments by Target Path\n(Comments from users with >{int(POLITICAL_MAJORITY_THRESHOLD*100)}% Consistency)', y=1.05, fontsize=16)
    g.set_axis_labels("Share of Comments (%)", "Newspaper Target Path")
    g.set_titles("{col_name}")
    
    # Add percentage labels to the bars
    for ax in g.axes.flat:
        for p in ax.patches:
            width = p.get_width()
            if width > 0:
                ax.annotate(f'{width:.0f}%', 
                            (width, p.get_y() + p.get_height() / 2.), 
                            ha='left', va='center', fontsize=10, color='black', xytext=(5, 0), 
                            textcoords='offset points')
                            
    plt.savefig('results/prof_writing_analytics/ideological_path_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Generating comprehensive comparison markdown report...")
    md_report = """# Political Intent: Astroturfers vs Normal Users

These reports directly compare the ideological consistency and exact targets of Professional Writers against normal users.

## 1. Overall Ideological Share (Left vs Right)
This chart displays the percentage breakdown of ideological leanings across highly partisan users (>80% consistency).
![Ideological Share Comparison](./ideological_share_comparison.png)

## 2. Ideological Share by Specific Political Path
For the top 10 most targeted newspaper categories, this chart breaks down the ideological proportion of the comments. It directly contrasts the behavior of normal users on those topics versus the professional astroturfers.
![Ideological Path Comparison](./ideological_path_comparison.png)
"""
    with open('results/prof_writing_analytics/political_comparison_report.md', 'w', encoding='utf-8') as f:
        f.write(md_report)

    print("Comparison analytics completely finished!")

if __name__ == '__main__':
    run()
