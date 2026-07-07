import pandas as pd
import numpy as np
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import entropy
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

tqdm.pandas()

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

def calc_formality(text):
    """
    Calculate the formality score of a text based on capitalization and punctuation.

    Args:
        text (str): The input text.

    Returns:
        float: The formality score.
    """
    if pd.isna(text) or len(text) == 0:
        return 0.0
    text = str(text)
    caps = sum(1 for c in text if c.isupper())
    punct = sum(1 for c in text if c in '.,!?;:')
    return (caps + punct) / len(text)

def main():
    """
    Execute the feature engineering pipeline.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "data")
    output_dir = os.path.join(data_dir, "prof_writing_analytics")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("1. Loading data...")
    posts = pd.read_csv(os.path.join(data_dir, "Posts.csv"))
    articles = pd.read_csv(os.path.join(data_dir, "Articles.csv"))
    
    # ---------------------------------------------------------
    # 1. TEMPORAL FEATURES
    # ---------------------------------------------------------
    print("2. Parsing dates and Temporal Features...")
    posts['CreatedAt'] = pd.to_datetime(posts['CreatedAt'], errors='coerce')
    articles['publishingDate'] = pd.to_datetime(articles['publishingDate'], errors='coerce')
    
    posts['day_of_week'] = posts['CreatedAt'].dt.dayofweek # 0=Mon, 6=Sun
    posts['hour'] = posts['CreatedAt'].dt.hour
    posts['is_weekday_9to5'] = ((posts['day_of_week'] < 5) & (posts['hour'] >= 9) & (posts['hour'] <= 17)).astype(int)
    
    print("Merging Posts and Articles...")
    merged = pd.merge(posts, articles[['ID_Article', 'publishingDate', 'Path']], on='ID_Article', how='left')
    
    merged['time_to_publish_mins'] = (merged['CreatedAt'] - merged['publishingDate']).dt.total_seconds() / 60.0
    merged['time_to_publish_mins'] = merged['time_to_publish_mins'].clip(lower=0) # replace negatives
    
    # ---------------------------------------------------------
    # 2. TOPIC TARGETING
    # ---------------------------------------------------------
    merged['Topic'] = merged['Path'].apply(safe_extract_topic)
    
    # ---------------------------------------------------------
    # 3. CONTENT ANALYSIS
    # ---------------------------------------------------------
    print("3. Calculating VADER Sentiment & Formality (this takes a moment)...")
    analyzer = SentimentIntensityAnalyzer()
    
    def get_vader(text):
        """
        Calculate VADER sentiment compound score for a text.

        Args:
            text (str): The text to analyze.

        Returns:
            float: The VADER compound sentiment score.
        """
        if pd.isna(text):
            return 0.0
        return analyzer.polarity_scores(str(text))['compound']
    
    merged['Body_str'] = merged['Body'].fillna('')
    # Sample a small chunk if testing, but doing full dataset here
    merged['sentiment'] = merged['Body_str'].progress_apply(get_vader)
    merged['formality'] = merged['Body_str'].progress_apply(calc_formality)
    
    # ---------------------------------------------------------
    # 4. VOTING & IMPACT
    # ---------------------------------------------------------
    merged['controversy'] = (merged['PositiveVotes'] * merged['NegativeVotes']) / (merged['PositiveVotes'] + merged['NegativeVotes'] + 1)
    merged['echo_chamber'] = merged['PositiveVotes'] / (merged['time_to_publish_mins'] + 1)
    
    # ---------------------------------------------------------
    # AGGREGATE TO USER LEVEL
    # ---------------------------------------------------------
    print("4. Aggregating user-level features...")
    user_features = merged.groupby('ID_User').agg(
        total_posts=('ID_Post', 'count'),
        perc_weekday_9to5=('is_weekday_9to5', 'mean'),
        first_mover_avg=('time_to_publish_mins', 'mean'),
        avg_controversy=('controversy', 'mean'),
        avg_echo_chamber=('echo_chamber', 'mean'),
        sentiment_std=('sentiment', 'std'),
        avg_formality=('formality', 'mean'),
        active_days=('CreatedAt', lambda x: x.dt.date.nunique())
    ).reset_index()
    
    user_features['posts_per_active_day'] = user_features['total_posts'] / user_features['active_days'].replace(0, 1)
    user_features['sentiment_std'] = user_features['sentiment_std'].fillna(0)
    
    # Topic Entropy
    print("Calculating Topic Entropy...")
    def calc_entropy(x):
        """
        Calculate topic entropy.

        Args:
            x (pd.Series): A series of topics.

        Returns:
            float: The calculated entropy.
        """
        counts = x.value_counts()
        return entropy(counts) if len(counts) > 1 else 0.0
    
    topic_entropy = merged.groupby('ID_User')['Topic'].apply(calc_entropy).reset_index(name='topic_entropy')
    user_features = pd.merge(user_features, topic_entropy, on='ID_User')
    
    # Semantic Similarity
    print("5. Calculating Semantic Similarity for highly active users (>=50 posts)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    active_users = user_features[user_features['total_posts'] >= 50]['ID_User'].tolist()
    sim_scores = []
    
    active_merged = merged[merged['ID_User'].isin(active_users)]
    grouped = active_merged.groupby('ID_User')
    
    for uid in tqdm(active_users, desc="Embedding Sentences"):
        texts = grouped.get_group(uid)['Body_str'].tolist()
        # Cap at 50 to prevent out of memory and extreme slow downs
        if len(texts) > 50:
            np.random.seed(42)
            texts = np.random.choice(texts, 50, replace=False).tolist()
            
        if len(texts) < 2:
            sim_scores.append(0.0)
            continue
            
        embeddings = model.encode(texts, show_progress_bar=False)
        sim_matrix = cosine_similarity(embeddings)
        n = sim_matrix.shape[0]
        if n > 1:
            avg_sim = (np.sum(sim_matrix) - n) / (n * (n - 1))
        else:
            avg_sim = 0.0
        sim_scores.append(avg_sim)
        
    sim_df = pd.DataFrame({'ID_User': active_users, 'semantic_similarity': sim_scores})
    user_features = pd.merge(user_features, sim_df, on='ID_User', how='left')
    user_features['semantic_similarity'] = user_features['semantic_similarity'].fillna(0.0)
    
    # Save user features
    output_path = os.path.join(output_dir, "user_features.csv")
    user_features.to_csv(output_path, index=False)
    print(f"Feature engineering complete. Saved to {output_path}")

if __name__ == "__main__":
    main()
