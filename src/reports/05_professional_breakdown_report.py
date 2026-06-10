import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run():
    print("Loading predictions data...")
    preds = pd.read_csv('data/prof_writing_analytics/predictions.csv')
    
    # We only need one row per user to count users
    if 'user_id' in preds.columns:
        preds.rename(columns={'user_id': 'ID_User'}, inplace=True)
        
    users = preds.drop_duplicates(subset=['ID_User']).copy()
    
    # Create the overall 'professional' flag
    users['is_professional'] = users[['is_professional_temporal', 
                                      'is_professional_topic', 
                                      'is_professional_content', 
                                      'is_professional_impact']].max(axis=1)
    
    total_users = len(users)
    normal_count = (users['is_professional'] == 0).sum()
    prof_count = (users['is_professional'] == 1).sum()
    
    # Counts by analytical approach
    count_temporal = users['is_professional_temporal'].sum()
    count_topic = users['is_professional_topic'].sum()
    count_content = users['is_professional_content'].sum()
    count_impact = users['is_professional_impact'].sum()
    
    print("Generating Breakdown Chart...")
    plt.figure(figsize=(10, 6))
    
    categories = ['Normal Users', 'Temporal\n(9-to-5)', 'Topic\n(Single-Issue)', 'Content\n(Copy-Paste)', 'Impact\n(Echo Chamber)']
    counts = [normal_count, count_temporal, count_topic, count_content, count_impact]
    
    # Use a specific color for Normal, and a palette for the heuristics
    colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728', '#9467bd']
    
    ax = sns.barplot(x=categories, y=counts, palette=colors)
    plt.title('User Breakdown: Normal vs. Professional Heuristics', fontsize=15, pad=15)
    plt.ylabel('Number of Unique Users')
    
    # Log scale if the difference is too massive (Normal users are likely huge)
    plt.yscale('log')
    plt.ylabel('Number of Unique Users (Log Scale)')
    
    # Add data labels
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{int(height):,}', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=11, color='black', xytext=(0, 5), 
                        textcoords='offset points')
            
    plt.tight_layout()
    plt.savefig('results/prof_writing_analytics/professional_breakdown.png', dpi=300)
    plt.close()

    print("Generating Breakdown Report...")
    report = f"""# Breakdown of Users: Normal vs. Professional Writers

This report details the exact number of users classified as "Normal" versus those classified as "Professional Writers" (Astroturfers), grouped by the specific analytical approach (heuristic) that caught them.

## Summary Counts
Out of **{total_users:,}** total unique users in the dataset:
* **Normal Users**: {normal_count:,} ({(normal_count/total_users)*100:.2f}%)
* **Professional Users**: {prof_count:,} ({(prof_count/total_users)*100:.2f}%)

*(Note: A professional user can be flagged by more than one heuristic simultaneously).*

## Breakdown by Analytical Approach
The {prof_count:,} professional users were flagged by the following detection pillars:

* **Impact (Echo Chamber)**: {count_impact:,} users
* **Topic (Single-Issue Hyperfocus)**: {count_topic:,} users
* **Content (Copy-Paste Behavior)**: {count_content:,} users
* **Temporal (9-to-5 Working Hours)**: {count_temporal:,} users

### Visualization
Because the number of normal users vastly outweighs the professional users, the chart below uses a logarithmic scale to properly display all groups side-by-side.

![User Breakdown](./professional_breakdown.png)

"""
    with open('results/prof_writing_analytics/professional_breakdown_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print("Report successfully generated!")

if __name__ == '__main__':
    run()
