"""
Configuration file for Political Intent Analysis (V2)
Optimized to avoid "Topic Traps" by focusing purely on ideological framing, 
pejoratives, and the Austrian context from 2003-2016.
"""

# Thresholds
POLITICAL_MAJORITY_THRESHOLD = 0.68  # +1 Standard Deviation (~68%) above expected value (50%)

# Lexicon Selection
ACTIVE_LEXICON = "crisis" # Options: "normal" or "crisis"

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
        "neoliberale", "neoliberalismus", "menschenverachtend", "soziale kälte", 
        "rechtsextrem", "kellernazi", "ausländerfeindlich", "fremdenfeindlich", 
        "rassistisch", "rassismus", "alltagsrassismus", "homophobie", 
        "bierzeltniveau", "stammtischniveau", "rückschrittlich", "sozialabbau", 
        "lohndumping", "ausbeutung", "rechter rand", "ausgrenzung", "wutbürger",
        "geistige brandstifter", "geistige brandstiftung", "hass im netz", 
        "hassposter", "braune rülpser", "postfaktisch", "faktenresistenz",
        
        # Positive Framing of the Left & VdB-Campaign (2016)
        "zivilgesellschaft", "menschenrechte", "solidarität", "soziale gerechtigkeit", 
        "weltoffen", "weltoffenheit", "vielfalt", "inklusion", "zusammenhalt", 
        "toleranz", "menschenwürde", "chancengleichheit", "pazifismus",
        "anstand", "haltung", "zivilcourage", "menschlichkeit",
        
        # Flucht-Framing 2015/16
        "schutzsuchende", "geflüchtete", "menschen auf der flucht", "fluchtursachen"
    ],
    
    "right_wing": [
        # Negative Framing against Left, Progressivism & Media
        "gutmenschen", "gutmensch", "linkslink", "linkslinke", "linksgrün",
        "bahnhofsklatscher", "willkommensklatscher", "teddybärenwerfer", 
        "systempresse", "lügenpresse", "rotfunk", "staatsfunk", "zwangsgebühren",
        "bobo", "bobos", "meinungsdiktatur", "gesinnungsterror", "gesinnungsdiktatur",
        "asylindustrie", "sozialromantik", "sozialromantiker", "multikulti", 
        "multikulti-wahn", "kaviarlinke", "salonkommunist", "verbotskultur", 
        "mainstreammedien", "kuscheljustiz", "ideologiegetrieben", "realitätsverweigerung", 
        "asylmissbrauch", "parallelgesellschaft", "kulturfremd",
        "neiddebatte", "neidgesellschaft", "altparteien", "systemparteien",
        "einheitsparteien", "genderwahn", "frühsexualisierung",
        
        # Migration & Hard Right Framing
        "asyltourismus", "sozialschmarotzer", "überfremdung", "islamisierung", 
        "umvolkung", "bevölkerungsaustausch", "asylflut", "e-card tourist", 
        "wirtschaftsflüchtling", "wirtschaftsmigrant", "scheinasylanten", 
        "asylforderer", "illegale einwanderung", "asylanten", "asylwerberheim",
        
        # Sarcasm 2015/2016 (Crucial for Discriminatory Power!)
        "fachkräfte", "goldstücke", "kulturbereicherer", "kulturelle bereicherung", 
        "raketenwissenschaftler", "merkel-gäste",
        
        # Positive Framing of the Right
        "leistungsträger", "eigenverantwortung", "patriotismus", "heimatliebe",
        "heimatschutz", "hausverstand", "innere sicherheit", "tradition", "leitkultur",
        "schweigende mehrheit", "familienwerte", "christliche werte", 
        "christliches abendland", "grenzschutz"
    ]
}

POLITICAL_LEXICON_CRISIS = {
    "left_wing": [
        "schutzsuchende", 
        "menschen auf der flucht",
        "geflüchtete",
        "menschlichkeit",
        "menschenrechte",
        "asyl ist ein grundrecht",
        "hassposter", 
        "geistige brandstiftung",
        "stammtisch",
    ],
    
    "right_wing": [
        "bahnhofsklatscher", 
        "willkommensklatscher",
        "asylflut", 
        "wirtschaftsflüchtlinge", 
        "asylforderer", 
        "kontrollverlust", 
        "obergrenze",
        "fachkräfte", 
        "goldstücke",
        "kulturbereicherer"
    ]
}

if ACTIVE_LEXICON == "crisis":
    CURRENT_LEXICON = POLITICAL_LEXICON_CRISIS
else:
    CURRENT_LEXICON = POLITICAL_LEXICON

