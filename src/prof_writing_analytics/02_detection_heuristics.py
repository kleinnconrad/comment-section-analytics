import pandas as pd
import os

def safe_extract_topic(path):
    """
    Safely extract the topic from an article path.

    Args:
        path (str): The path string from the article.

    Returns:
        str: The extracted topic.
    """
    if pd.isna(path):
        return "Unknown"
    parts = str(path).split('/')
    if len(parts) > 1:
        return parts[1]
    return parts[0]

def main():
    """
    Apply heuristics to detect professional writers.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "data")
    output_dir = os.path.join(data_dir, "prof_writing_analytics")
    
    print("Loading user features and original posts...")
    users = pd.read_csv(os.path.join(output_dir, "user_features.csv"))
    posts = pd.read_csv(os.path.join(data_dir, "Posts.csv"))
    articles = pd.read_csv(os.path.join(data_dir, "Articles.csv"))
    
    # Calculate Impact percentiles
    p90_controversy = users['avg_controversy'].quantile(0.90)
    p90_echo = users['avg_echo_chamber'].quantile(0.90)
    
    # ---------------------------------------------------------
    # APPLY HEURISTICS
    # ---------------------------------------------------------
    print("Applying heuristics...")
    
    # 1. Temporal & Behavioral
    # High volume, strict 9-to-5, early commenter
    users['is_professional_temporal'] = (
        (users['posts_per_active_day'] >= 10) & 
        (users['perc_weekday_9to5'] >= 0.75) & 
        (users['first_mover_avg'] <= 60)
    ).astype(int)
    
    # 2. Topic Targeting
    # High volume but very low entropy (hyper-focused)
    users['is_professional_topic'] = (
        (users['total_posts'] >= 10) & 
        (users['topic_entropy'] <= 0.2)
    ).astype(int)
    
    # 3. Content Analysis
    # Copy-pasting (moderate similarity) OR robotic sentiment (low variance) with high formality
    p80_formality = users['avg_formality'].quantile(0.80)
    users['is_professional_content'] = (
        (users['semantic_similarity'] >= 0.5) |
        ((users['sentiment_std'] <= 0.1) & (users['avg_formality'] >= p80_formality) & (users['total_posts'] >= 5))
    ).astype(int)
    
    # 4. Voting & Impact
    # Consistently high controversy or echo chamber metrics
    users['is_professional_impact'] = (
        (users['avg_controversy'] >= p90_controversy) | 
        (users['avg_echo_chamber'] >= p90_echo)
    ).astype(int)
    
    # Ensure they have a minimum number of posts to be flagged to avoid noise
    min_posts_mask = users['total_posts'] >= 5
    for col in ['is_professional_temporal', 'is_professional_topic', 'is_professional_content', 'is_professional_impact']:
        users[col] = (users[col] & min_posts_mask).astype(int)
    
    # ---------------------------------------------------------
    # MERGE BACK TO POSTS & FORMAT OUTPUT
    # ---------------------------------------------------------
    print("Merging back to post level...")
    # Get topics for posts
    posts_merged = pd.merge(posts, articles[['ID_Article', 'Path']], on='ID_Article', how='left')
    posts_merged['topic_category'] = posts_merged['Path'].apply(safe_extract_topic)
    
    # Join the user-level flags to the posts
    cols_to_keep = ['ID_User', 'is_professional_temporal', 'is_professional_topic', 'is_professional_content', 'is_professional_impact']
    final_df = pd.merge(posts_merged, users[cols_to_keep], on='ID_User', how='left')
    
    # Rename columns to match exact user request
    final_df = final_df.rename(columns={
        'ID_User': 'user_id',
        'CreatedAt': 'timestamp',
        'ID_Article': 'article',
        'Body': 'comment'
    })
    
    output_cols = [
        'user_id', 'timestamp', 'article', 'topic_category', 'comment',
        'is_professional_temporal', 'is_professional_topic', 
        'is_professional_content', 'is_professional_impact'
    ]
    
    final_df = final_df[output_cols]
    
    # Fill NAs for users that might not have generated features (e.g. no body)
    flag_cols = ['is_professional_temporal', 'is_professional_topic', 'is_professional_content', 'is_professional_impact']
    final_df[flag_cols] = final_df[flag_cols].fillna(0).astype(int)
    
    output_file = os.path.join(output_dir, "predictions.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Heuristics applied. Final analytical table saved to {output_file}")

if __name__ == "__main__":
    main()
