"""
Configuration file for Political Intent Analysis (V2)
Optimized to avoid "Topic Traps" by focusing purely on ideological framing, 
pejoratives, and the Austrian context from 2003-2016.
"""

# Thresholds
POLITICAL_MAJORITY_THRESHOLD = 0.80  # A user must have > 80% of their political comments lean one way

# ==============================================================================
# AUSTRIAN POLITICAL LEXICON (STRICT FRAMING)
# Rule: NO party names (FPÖ, SPÖ, Grüne) and NO neutral topics (Asyl, Grenzen).
# We ONLY match how one side explicitly attacks or frames the other side.
# This maximizes separation because these terms are rarely used neutrally.
# ==============================================================================

POLITICAL_LEXICON = {
    "left_wing": [
        # Framing the Right & Conservative Policies
        "brauner sumpf", "ewiggestrige", "rechtspopulisten", "rechtspopulismus",
        "hetzer", "hetze", "spalter", "spaltung", "neoliberale", "neoliberalismus",
        "menschenverachtend", "soziale kälte", "angstmache", "rechtsextrem", 
        "kellernazi", "ausländerfeindlich", "fremdenfeindlich", "rassistisch", 
        "rassismus", "alltagsrassismus", "homophobie", "bierzelt", "rückschrittlich",
        "sozialabbau", "lohndumping", "ausbeutung", "rechter rand", "reichtumssteuer", 
        "erbschaftssteuer", "vermögenssteuer"
    ],
    
    "right_wing": [
        # Framing the Left, Progressivism & Migration
        "gutmenschen", "linkslink", "linkslinke", "bahnhofsklatscher", 
        "willkommensklatscher", "systempresse", "lügenpresse", "rotfunk", 
        "staatsfunk", "bobo", "bobos", "genderwahn", "meinungsdiktatur", 
        "gesinnungsterror", "asylindustrie", "sozialromantik", "sozialromantiker", 
        "multikulti-wahn", "asyltourismus", "sozialschmarotzer", "überfremdung", 
        "islamisierung", "umvolkung", "asylflut", "e-card tourist", "kaviarlinke", 
        "salonkommunist", "verbotskultur", "mainstreammedien", "wirtschaftsflüchtling",
        "kuscheljustiz"
    ]
}

"""
BLACKLIST / DO NOT USE (For Documentation)
Words that trigger False Positives because opponents use them to criticize each other or because they are generally neutral terms that are over-represented:
"fpö", "övp", "spö", "grüne", "strache", "faymann", "asyl", "ausländer", "grenze", "islam",
"politik", "regierung", "kanzler", "partei", "wahl", "wähler", "volk", "österreich", "europa",
"demokratie", "recht", "gesetz", "staat", "steuer", "wirtschaft", "geld", "krise", "problem"
"""
