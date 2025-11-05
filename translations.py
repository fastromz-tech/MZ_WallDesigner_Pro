# translations.py
# English / Serbian translation dictionary

translations = {
    "EN": {
        "app_title": "MZ WALL DESIGNER PRO v2.0",
        "subtitle": "Professional wall design and analysis software",
        "help": "Upload your wall drawing (.png or .jpg) to generate the full 2D & 3D layout, calculations, and block summary.",
        "upload_label": "Upload wall image",
        "generate_button": "Generate layout",
        "language": "Language",
        "calc_section": "Calculation results",
        "wall_area": "Wall area",
        "wall_volume": "Wall volume",
        "mortar_volume": "Mortar volume",
        "wall_weight": "Wall weight",
        "block_summary": "Block summary",
        "admin_panel": "Admin Panel",
        "logout": "Logout"
    },
    "SR": {
        "app_title": "MZ WALL DESIGNER PRO v2.0",
        "subtitle": "Profesionalni softver za projektovanje i analizu zidova",
        "help": "Učitaj crtež zida (.png ili .jpg) da bi generisao kompletan 2D i 3D prikaz, proračune i pregled blokova.",
        "upload_label": "Učitaj sliku zida",
        "generate_button": "Generiši raspored",
        "language": "Jezik",
        "calc_section": "Rezultati proračuna",
        "wall_area": "Površina zida",
        "wall_volume": "Zapremina zida",
        "mortar_volume": "Zapremina maltera",
        "wall_weight": "Masa zida",
        "block_summary": "Pregled blokova",
        "admin_panel": "Admin panel",
        "logout": "Odjavi se"
    }
}

def t(key, lang="EN"):
    """Translation helper."""
    return translations.get(lang, translations["EN"]).get(key, key)
