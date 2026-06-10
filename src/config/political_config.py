"""
Configuration file for Political Intent Analysis
"""

# Thresholds
POLITICAL_MAJORITY_THRESHOLD = 0.80  # A user must have > 80% of their political comments lean one way to be classified

# Austrian Political Lexicon
# Used to determine the intent of a specific comment based on keyword matching
POLITICAL_LEXICON = {
    "left_wing": [
        "solidarität", "umverteilung", "sozialabbau", "klimaschutz", "menschenrechte", 
        "mindestsicherung", "gerechtigkeit", "reichtumssteuer", "erbschaftssteuer", 
        "hetze", "rassismus", "feminismus", "gleichberechtigung", "grundsicherung",
        "kapitalismus", "ausbeutung", "klassengesellschaft", "neoliberal", "spö", "grüne",
        "toleranz", "antifa", "sozial", "gewerkschaft", "arbeiter", "menschlichkeit",
        "menschenwürde", "vielfalt", "inklusion", "zusammenhalt", "chancengleichheit",
        "weltoffen", "bunt", "zivilgesellschaft", "verteilungsgerechtigkeit", "pazifismus"
    ],
    "right_wing": [
        "gutmenschen", "asylant", "systempresse", "linkslinke", "wirtschaftsflüchtling", 
        "leistungsträger", "heimatschutz", "kriminelle ausländer", "islamisierung", 
        "leitkultur", "grenzschutz", "sicherheit", "steuern senken", "sozialschmarotzer",
        "mainstreammedien", "meinungsdiktatur", "genderwahn", "umvolkung", "überfremdung",
        "fpö", "övp", "hc strache", "ausländer", "heimat", "grenzen", "familie",
        "kultur", "tradition", "patriotismus", "werte", "identität", "christlich",
        "abendland", "wirtschaftswachstum", "eigenverantwortung", "volk", "nation"
    ]
}
