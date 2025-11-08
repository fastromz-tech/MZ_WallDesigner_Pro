import streamlit as st

# =========================================================
# MZ_WALLDESIGNER_PRO – WALL ANALYZER (manual geometry mode)
# =========================================================
# Autor: Moca Zizic & GPT-5
# Verzija: 2025.11
# Opis:
#  Ova verzija omogućava ručni unos dimenzija zida i otvora.
#  Na osnovu toga vraća koordinate zidne površine i svake praznine (prozora/vrata).
#  Kasnije će se dopuniti automatskom analizom slike (OpenCV + pdf2image).
# =========================================================


def get_manual_wall_data():
    """
    Interaktivni unos geometrije zida i otvora putem Streamlit UI-ja.
    Sve vrednosti su u centimetrima (cm).
    """
    st.subheader("🧱 Ručni unos dimenzija zida i otvora")

    # --- Unos dimenzija zida ---
    st.markdown("#### Dimenzije zida")
    wall_width = st.number_input("Širina zida (cm)", min_value=100.0, value=500.0, step=10.0)
    wall_height = st.number_input("Visina zida (cm)", min_value=100.0, value=300.0, step=10.0)

    # --- Unos broja otvora ---
    st.markdown("#### Prozori i vrata")
    num_openings = st.number_input("Broj otvora (prozori/vrata)", min_value=0, max_value=10, value=2, step=1)

    openings = []
    for i in range(int(num_openings)):
        st.markdown(f"##### Otvor {i+1}")
        w = st.number_input(f"• Širina otvora {i+1} (cm)", min_value=10.0, value=100.0, step=5.0, key=f"ow_{i}")
        h = st.number_input(f"• Visina otvora {i+1} (cm)", min_value=10.0, value=120.0, step=5.0, key=f"oh_{i}")
        x = st.number_input(
            f"• X pozicija donjeg levog ugla (cm, od zida 0.0,0.0)", 
            min_value=0.0, value=50.0, step=5.0, key=f"ox_{i}"
        )
        y = st.number_input(
            f"• Y pozicija donjeg levog ugla (cm, od zida 0.0,0.0)",
            min_value=0.0, value=50.0, step=5.0, key=f"oy_{i}"
        )
        openings.append({"id": i + 1, "x": x, "y": y, "w": w, "h": h, "type": "opening"})

    # --- Rezime podataka ---
    wall_data = {
        "dimensions": {"width_cm": wall_width, "height_cm": wall_height},
        "openings": openings,
    }

    st.success("✅ Podaci o zidu su uneti.")
    st.json(wall_data)
    return wall_data


def extract_wall_data(input_mode="manual", image=None, pdf_path=None):
    """
    Glavna funkcija za dobijanje podataka o zidu.
    Trenutno podržava samo 'manual' unos.
    """
    if input_mode == "manual":
        wall_data = get_manual_wall_data()

        # Generišemo osnovni blok (pravougaonik zida bez otvora)
        width = wall_data["dimensions"]["width_cm"]
        height = wall_data["dimensions"]["height_cm"]

        wall_rect = {"x": 0, "y": 0, "w": width, "h": height, "type": "wall"}

        return {
            "wall": wall_rect,
            "openings": wall_data["openings"],
            "dimensions": wall_data["dimensions"],
        }

    else:
        st.error("Trenutno je dostupan samo ručni unos. Automatska analiza slike biće dodata kasnije.")
        return None


# =========================================================
# Test mod (ako se fajl pokreće direktno, a ne kroz Streamlit)
# =========================================================
if __name__ == "__main__":
    import json

    print("Pokrećem test ručnog unosa zida (CLI mode)...")
    test_data = {
        "dimensions": {"width_cm": 600, "height_cm": 300},
        "openings": [
            {"x": 50, "y": 0, "w": 100, "h": 210, "type": "door"},
            {"x": 300, "y": 90, "w": 120, "h": 120, "type": "window"}
        ],
    }
    print(json.dumps(test_data, indent=2))
