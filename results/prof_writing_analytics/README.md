# Political Intent & Target Analytics

This directory contains the final analytics and charts mapping the specific targets of political astroturfers (professional writers) and comparing them against normal users. 

## Methodology: Political Intent Analysis
Instead of classifying users based on the political leaning of the newspaper article they comment on (which can be flawed since users frequently argue with articles they disagree with), we analyze the actual **raw text of the comments** to determine ideological intent.

### 1. NLP Lexicon Matching
The text of over 1 million comments is parsed against an extensive **Austrian Political Lexicon** (configured in `src/config/political_config.py`). 
* **Left-Wing Lexicon**: Includes hard political keywords (e.g., `spö`, `grüne`, `sozialabbau`, `umverteilung`, `reichtumssteuer`) as well as soft cultural keywords (e.g., `menschlichkeit`, `menschenwürde`, `vielfalt`, `toleranz`, `zusammenhalt`).
* **Right-Wing Lexicon**: Includes hard political keywords (e.g., `fpö`, `övp`, `steuern senken`, `grenzschutz`) as well as soft cultural keywords (e.g., `familie`, `kultur`, `heimat`, `tradition`, `patriotismus`, `leitkultur`).

A comment is flagged as Left or Right if its text strictly contains more keywords from one ideology than the other.

### 2. The 80% Ideological Consistency Threshold
Users are not assigned a political spectrum lightly. We enforce an **extreme ideological consistency threshold**.
For a user to be classified as a "Highly Partisan Left-Wing Writer" or a "Highly Partisan Right-Wing Writer", **more than 80%** of their politically-relevant comments must lean strictly in that one direction. Users who frequently jump back and forth are filtered out.

### 3. Target Grouping & Timelines
Once a user is confidently classified as a strict partisan, **all of their comments** (including neutral ones) are mapped back to the specific `Path` (category) of the newspaper they were commenting on. In the generated reports, every comment written by a classified user is counted as a comment from that respective ideological group. 

This user-centric approach allows us to see exactly *what* these partisan groups care about and target overall, even when they participate in seemingly non-political discussions without explicitly using framing keywords. The results are generated both in `total` across the entire corpus, and sliced chronologically `by year`.

## Output Reports

* **`political_timeline.md`**: The aggregated chronological report showing what paths the Highly Partisan **Professional Writers** (Astroturfers) targeted from 2014 to 2016.
* **`political_timeline_normal.md`**: The aggregated chronological report showing what paths the Highly Partisan **Normal Users** targeted.
* **`political_spectrum_targets_XXXX.png`**: The individual yearly diagrams generated for presentations.
* **`detailed_paths.png`** / **`detailed_paths_nonpol.png`**: The overarching diagrams mapping all the specific targets.
