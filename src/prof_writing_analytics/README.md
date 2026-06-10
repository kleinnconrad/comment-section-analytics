# Professional Writing & Astroturfing Detection

This module implements a set of heuristics based anomaly detection to identify professional writers or astroturfing accounts in the Million Post Corpus.

## Methodology

### 1. Temporal & Behavioral Analysis (`is_professional_temporal`)
Detects users treating posting like a 9-to-5 job.
* **Posts per Active Day**: Total posts divided by the number of unique days the user was active.
* **Weekday 9-to-5 Ratio**: Percentage of posts made strictly between Monday-Friday, 09:00-17:00.
* **First Mover Advantage**: The average time (in minutes) between an article's publication and the user's comment. 
* **Threshold**: Users with >= 10 posts/active day AND >= 75% posts in 9-to-5 AND average response time <= 60 minutes.

### 2. Topic Targeting (`is_professional_topic`)
Detects single-issue accounts that only target specific topics.
* **Topic Entropy**: Shannon Entropy of the top-level article paths the user comments on. 
* **Threshold**: Users with >= 10 total posts AND Entropy <= 0.2.

### 3. Content Analysis via NLP (`is_professional_content`)
Detects copy-pasting or highly formalized extreme sentiment.
* **Semantic Similarity**: Uses `all-MiniLM-L6-v2` to compute average cosine similarity of a user's posts.
* **Sentiment Extremity**: Standard deviation of VADER compound sentiment scores.
* **Formality Approximation**: Ratio of capital letters and punctuation marks to total text length.
* **Threshold**: Users with semantic similarity >= 0.7 OR (sentiment std <= 0.1 AND high formality AND >= 5 posts).

### 4. Voting & Impact (`is_professional_impact`)
Detects high-impact and highly controversial users.
* **Controversy Score**: `(Pos * Neg) / (Pos + Neg + 1)`
* **Echo Chamber**: `PosVotes / (Time_Since_Publish_Mins + 1)`
* **Threshold**: Above the 90th percentile in either metric for the entire dataset.

## Execution

Run the pipeline in order:
1. `python 01_feature_engineering.py` -> Outputs `user_features.csv`
2. `python 02_detection_heuristics.py` -> Outputs `predictions.csv` (The final analytical table)
3. `python 03_evaluate_metrics.py` -> Outputs `model_quality_metrics.json`

## Evaluation
Since there are no definitive ground truth labels for "astroturfers", we use the `Newspaper_Staff` table as a proxy for Professional Writers. The evaluation scripts compute precision and recall metrics on how well our unsupervised heuristics overlap with the known professional staff. Note that precision may naturally be low, because successful astroturfers (True Positives in reality) are not in the Staff table (False Positives in our evaluation proxy).
