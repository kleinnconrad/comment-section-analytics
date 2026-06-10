"""
Configuration file for Political Intent Analysis (V2)
Optimized to avoid "Topic Traps" by focusing purely on ideological framing, 
pejoratives, and the Austrian context from 2003-2016.
"""

# Thresholds
POLITICAL_MAJORITY_THRESHOLD = 0.68  # +1 Standard Deviation (~68%) above expected value (50%)

# ==============================================================================
# AUSTRIAN POLITICAL LEXICON (MODERATE FRAMING)
# Rule: NO party names (FPÖ, SPÖ, Grüne) and NO neutral topics (Asyl, Grenzen).
# We match how one side frames the other, including both harsh slurs and 
# more moderate, slightly partisan vocabulary.
# ==============================================================================

POLITICAL_LEXICON = {
    "left_wing": [
        # Negative Framing against Right & Conservative Policies
        "brauner sumpf", "ewiggestrige", "rechtspopulisten", "rechtspopulismus",
        "hetzer", "hetze", "spalter", "spaltung", "neoliberale", "neoliberalismus",
        "menschenverachtend", "soziale kälte", "angstmache", "rechtsextrem", 
        "kellernazi", "ausländerfeindlich", "fremdenfeindlich", "rassistisch", 
        "rassismus", "alltagsrassismus", "homophobie", "bierzelt", "rückschrittlich",
        "sozialabbau", "lohndumping", "ausbeutung", "rechter rand", "reichtumssteuer", 
        "erbschaftssteuer", "vermögenssteuer", "klientelpolitik", "profitgier", 
        "populismus", "ausgrenzung", "steuergeschenke", "kürzungspolitik", 
        "privatisierung", "ungerechtigkeit", "wutbürger", "stammtisch",
        
        # Positive Framing of the Left
        "zivilgesellschaft", "neid", "neiddebatte", "menschenrechte", "solidarität",
        "soziale gerechtigkeit", "gerechtigkeit", "weltoffen", "weltoffenheit", 
        "vielfalt", "inklusion", "zusammenhalt", "gleichberechtigung", "toleranz", 
        "menschenwürde", "chancengleichheit", "pazifismus", "umverteilung"
    ],
    
    "right_wing": [
        # Negative Framing against Left, Progressivism & Migration
        "gutmenschen", "linkslink", "linkslinke", "bahnhofsklatscher", 
        "willkommensklatscher", "systempresse", "lügenpresse", "rotfunk", 
        "staatsfunk", "bobo", "bobos", "genderwahn", "meinungsdiktatur", 
        "gesinnungsterror", "asylindustrie", "sozialromantik", "sozialromantiker", 
        "multikulti-wahn", "asyltourismus", "sozialschmarotzer", "überfremdung", 
        "islamisierung", "umvolkung", "asylflut", "e-card tourist", "kaviarlinke", 
        "salonkommunist", "verbotskultur", "mainstreammedien", "wirtschaftsflüchtling",
        "kuscheljustiz", "bevormundung", "ideologiegetrieben", "realitätsverweigerung", 
        "naivität", "gleichmacherei", "schuldenpolitik", "asylmissbrauch", 
        "parallelgesellschaft", "steuerwahn", "kulturfremd",
        
        # Positive Framing of the Right
        "leistungsträger", "eigenverantwortung", "patriotismus", "heimatliebe",
        "heimatschutz", "hausverstand", "sicherheit", "tradition", "leitkultur",
        "schweigende mehrheit", "familienwerte", "christliche werte", 
        "christliches abendland", "normalverdiener", "wirtschaftswachstum"
    ]
}

"""
BLACKLIST / DO NOT USE (For Documentation)
Words that trigger False Positives because opponents use them to criticize each other:
"fpö", "övp", "spö", "grüne", "strache", "faymann", "asyl", "ausländer", "grenze", "islam"
"""
