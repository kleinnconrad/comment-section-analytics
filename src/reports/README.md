# Million Post Analytics: Reports

This directory contains scripts that process the categorized prediction results to generate plots, visual analytics, and markdown reports.

## Political Intent Reports

Currently, three main reports are generated:
- `01_political_intent_analysis.py`: Analyzes the ideological consistency of professional astroturfers (for the years 2015 & 2016).
- `03_political_intent_analysis_normal.py`: Analyzes the ideological consistency of normal commenters (for the years 2015 & 2016).
- `04_political_intent_comparison.py`: Compares the distributions and targeted paths of both groups directly.

## Lexicon Configuration

The political intent analysis is based on keyword/pejorative matching defined in `src/config/political_config.py`.

You can toggle between different lexicons by modifying the `ACTIVE_LEXICON` variable in `political_config.py`:

```python
# Lexicon Selection
ACTIVE_LEXICON = "crisis" # Options: "normal" or "crisis"
```

- `"normal"`: Uses the extensive standard lexicon spanning from 2003 to 2016 (`POLITICAL_LEXICON`).
- `"crisis"`: Uses an alternative, highly focused lexicon centered around the 2015/2016 migration crisis and specific related pejoratives (`POLITICAL_LEXICON_CRISIS`).

Changing this switch will automatically update the dictionary used by the `01`, `03`, and `04` report generation scripts.
