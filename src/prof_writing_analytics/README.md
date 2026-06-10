# Professional Writing & Astroturfing Detection

This module implements a set of heuristics based anomaly detection to identify professional writers or astroturfing accounts in the Million Post Corpus.

## Detailed Methodology & Feature Engineering

The pipeline processes the raw `Posts` and `Articles` tables to compute a set of continuous features, which are then converted into binary flags based on strict anomaly thresholds. 

### 1. Temporal & Behavioral Analysis (`is_professional_temporal`)
Detects users treating posting like a rigid 9-to-5 job or utilizing automated bursting.
* **Posts per Active Day**: Calculated by taking the total `COUNT(ID_Post)` divided by the number of unique calendar dates the user was active. 
* **Weekday 9-to-5 Ratio**: We extract the day of week and hour from `CreatedAt`. A post is marked `1` if it occurred Monday-Friday between 09:00 and 17:59. We take the mean of this flag per user.
* **First Mover Advantage**: We calculate the difference in minutes between the `Articles.publishingDate` and the `Posts.CreatedAt`. We clip negative values to 0. We take the mean time-to-publish for all posts by the user.
* **Threshold**: Flagged as `1` if the user averages `>= 10` posts per active day AND `>= 75%` of their total posts strictly occur during weekday business hours AND their average response time to new articles is `<= 60` minutes.

### 2. Topic Targeting (`is_professional_topic`)
Detects "single-issue" accounts that aggressively target specific topics and ignore the rest of the newspaper.
* **Category Extraction**: We parse the `Articles.Path` column (e.g., `Newsroom/Sports/Motorsports/Formula 1`). We split by `/` and extract the highest-level category (e.g., `Sports`). 
* **Topic Entropy Calculation**: For every user, we calculate the distribution of their posts across these top-level categories. We calculate the mathematical Shannon Entropy of this distribution using `scipy.stats.entropy`. A user who posts 100% of the time in `Politics` will have an entropy of `0.0`. A user posting evenly across 10 categories will have high entropy.
* **Threshold**: Flagged as `1` if the user has `>= 10` total posts AND their Shannon Entropy is `<= 0.2` (indicating extreme hyper-focus on a single topic).

### 3. Content Analysis via NLP (`is_professional_content`)
Detects copy-pasting of PR scripts, extreme polarization, or uncharacteristically high formality compared to normal internet slang.
* **Semantic Similarity (Copy-Paste)**: Instead of older techniques like Doc2Vec or Gensim, this pipeline uses a modern Transformer architecture. Specifically, we use the `sentence-transformers` library to load `all-MiniLM-L6-v2`, a fast, distilled BERT model. We embed a sample of up to 50 posts per user, calculate a Cosine Similarity matrix across their own posts, and take the average of the off-diagonal similarities.
  * *Algorithm Details*: Unlike Doc2Vec's shallow neural network, this model relies on a deep **Transformer** network utilizing a **Self-Attention Mechanism**. Using matrix multiplication (Query, Key, and Value matrices), the network compares every word in a sentence to every other word simultaneously to build dynamic, context-aware representations. The data is passed through 6 deep Feed-Forward layers (the Encoder), outputting a highly refined vector for every token. Finally, the model uses **Mean Pooling**—calculating the mathematical average of all individual word vectors—to compress the output into a single, comprehensive 384-dimensional vector representing the entire post.
* **Sentiment Extremity**: We run `vaderSentiment` (Valence Aware Dictionary and sEntiment Reasoner) on every post's body. VADER is a lexicon and rule-based sentiment analysis tool specifically attuned to social media text. It relies on a dictionary of sentiment-heavy words but also understands grammatical rules (like capitalization, exclamation marks, emojis, and modifiers like "very"). It outputs a normalized `compound` score between -1.0 (extremely negative) and +1.0 (extremely positive). We calculate the Standard Deviation of this score per user. A standard deviation near `0.0` means the user is robotic and never breaks character from their extreme sentiment.
* **Formality Approximation**: We calculate a formality score by summing the number of uppercase characters and specific punctuation marks (`.,!?;:`), divided by the total string length.
* **Threshold**: Flagged as `1` if semantic similarity is `>= 0.70` (they are copy-pasting the exact same talking points). Alternatively, flagged as `1` if their sentiment standard deviation is `<= 0.1` AND their average formality is in the top 80th percentile for the entire corpus AND they have `>= 5` posts.

### 4. Voting & Impact (`is_professional_impact`)
Detects accounts generating massive polarization or utilizing "echo chambers" (coordinated upvote rings).
* **Controversy Score**: Calculated as `(PositiveVotes * NegativeVotes) / (PositiveVotes + NegativeVotes + 1)`. This metric heavily penalizes posts that just get upvotes or just downvotes, and rewards posts that trigger massive amounts of *both*.
* **Echo Chamber Score**: Calculated as `PositiveVotes / (Time_Since_Publish_Mins + 1)`. Detects posts that accrue an impossible number of upvotes relative to how late they were posted after the article's publication.
* **Threshold**: Flagged as `1` if the user's average controversy score OR their average echo chamber score ranks in the top `90th percentile` among all users.

## Execution

Run the pipeline in order:
1. `python 01_feature_engineering.py` -> Outputs `user_features.csv`
2. `python 02_detection_heuristics.py` -> Outputs `predictions.csv` (The final analytical table)
3. `python 03_evaluate_metrics.py` -> Outputs `model_quality_metrics.json`

## Evaluation
Since there are no definitive ground truth labels for "astroturfers", we use the `Newspaper_Staff` table as a proxy for Professional Writers. The evaluation scripts compute precision and recall metrics on how well our unsupervised heuristics overlap with the known professional staff. Note that precision may naturally be low, because successful astroturfers (True Positives in reality) are not in the Staff table (False Positives in our evaluation proxy).

## Execution Performance
This pipeline analyzes over 1,000,000 posts. Due to the heavy NLP calculations (VADER Sentiment and Sentence-Transformers embeddings), performance is heavily dependent on hardware.

- **Hardware**: 11th Gen Intel(R) Core(TM) i7-1195G7 @ 2.90GHz with 16 GB RAM
- **Execution Time**: ~1.5 hours (with the semantic similarity active user threshold set to >= 50 posts)
