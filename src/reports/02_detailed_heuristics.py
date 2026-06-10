import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run():
    print("Loading databases for detailed reports...")
    conn = sqlite3.connect('db/corpus.sqlite3')
    preds = pd.read_csv('data/prof_writing_analytics/predictions.csv')
    features = pd.read_csv('data/prof_writing_analytics/user_features.csv')
    
    preds.rename(columns={'user_id': 'ID_User'}, inplace=True)
    if 'y_pred_any' not in preds.columns:
        preds['y_pred_any'] = preds[['is_professional_temporal', 'is_professional_topic', 'is_professional_content', 'is_professional_impact']].max(axis=1)

    users = preds.drop_duplicates(subset=['ID_User']).copy()
    
    total_users = len(users)
    total_posts = len(preds)
    
    # Calculate Absolutes and Ratios
    heuristics = {
        'Temporal': preds['is_professional_temporal'].sum(),
        'Topic': preds['is_professional_topic'].sum(),
        'Content': preds['is_professional_content'].sum(),
        'Impact': preds['is_professional_impact'].sum()
    }
    
    # Plotting users
    users_merged = pd.merge(users, features, on='ID_User', how='left')
    user_counts = [
        users_merged['is_professional_temporal'].sum(),
        users_merged['is_professional_topic'].sum(),
        users_merged['is_professional_content'].sum(),
        users_merged['is_professional_impact'].sum(),
        users_merged['y_pred_any'].sum()
    ]
    labels = ['Temporal\n(9-to-5)', 'Topic\n(Single-Issue)', 'Content\n(Copy-Paste)', 'Impact\n(Echo Chamber)', 'Total\nFlagged']
    
    print("Generating Detailed Heuristics Bar Chart...")
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(x=labels, y=user_counts, palette='viridis')
    plt.title('Professional Writers by Heuristic Approach (Absolute & Ratio)', fontsize=15, pad=20)
    plt.ylabel('Number of Unique Users Flagged')
    
    # Add absolute numbers and ratios to bars
    for i, p in enumerate(ax.patches):
        abs_val = int(p.get_height())
        ratio = (abs_val / total_users) * 100
        ax.annotate(f'{abs_val:,}\n({ratio:.2f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=12, color='black', xytext=(0, 5), 
                    textcoords='offset points')
                    
    plt.tight_layout()
    plt.savefig('results/prof_writing_analytics/heuristic_breakdown_ratios.png', dpi=300)
    plt.close()
    
    # Do the same for posts
    post_counts = [
        preds['is_professional_temporal'].sum(),
        preds['is_professional_topic'].sum(),
        preds['is_professional_content'].sum(),
        preds['is_professional_impact'].sum(),
        preds['y_pred_any'].sum()
    ]
    
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(x=labels, y=post_counts, palette='mako')
    plt.title('Flagged Comments by Heuristic Approach (Absolute & Ratio)', fontsize=15, pad=20)
    plt.ylabel('Number of Flagged Comments')
    
    # Add absolute numbers and ratios to bars
    for i, p in enumerate(ax.patches):
        abs_val = int(p.get_height())
        ratio = (abs_val / total_posts) * 100
        ax.annotate(f'{abs_val:,}\n({ratio:.2f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=12, color='black', xytext=(0, 5), 
                    textcoords='offset points')
                    
    plt.tight_layout()
    plt.savefig('results/prof_writing_analytics/post_breakdown_ratios.png', dpi=300)
    plt.close()

    print("Generating Detailed Advanced Report...")
    report = f"""# Advanced Reporting & Political Intent Analysis

## 1. Detailed Heuristic Breakdowns (Absolute & Ratio)

We analyzed exactly how many unique users and individual comments triggered each of our four anomaly detection heuristics. The charts below display the absolute counts alongside their percentage of the total dataset.

### Users Flagged
*(Total Unique Users in Database: {total_users:,})*
![User Breakdown](./heuristic_breakdown_ratios.png)

### Comments Flagged
*(Total Comments in Database: {total_posts:,})*
![Post Breakdown](./post_breakdown_ratios.png)
"""
    with open('results/prof_writing_analytics/advanced_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("Detailed report generated successfully.")

if __name__ == '__main__':
    run()
