#!/usr/bin/env python3
"""
Photo URL Tester and Fixer for Star Carr
Run this locally to test all photo URLs and get replacements for broken ones.

Usage:
    pip install requests
    python test_photos.py
"""

import requests

# All photo URLs from config.py
URLS_TO_TEST = {
    # Terrain photos
    "deep_water": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Lac_Pavin_-_img_42825.jpg/320px-Lac_Pavin_-_img_42825.jpg",
    "shallow_water": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Canoeing_on_the_Chassahowitzka_River.jpg/320px-Canoeing_on_the_Chassahowitzka_River.jpg",
    "reed_bed": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phragmites_australis_Cam.jpg/320px-Phragmites_australis_Cam.jpg",
    "wetland": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Wetland_at_Sunset.jpg/320px-Wetland_at_Sunset.jpg",
    "carr_woodland": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Alnus_glutinosa_008.jpg/320px-Alnus_glutinosa_008.jpg",
    "birch_woodland": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Birch_trees_in_Finland.JPG/320px-Birch_trees_in_Finland.JPG",
    "mixed_woodland": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Deciduous_forest_in_autumn.jpg/320px-Deciduous_forest_in_autumn.jpg",
    "grassland": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Meadow_in_early_summer.jpg/320px-Meadow_in_early_summer.jpg",
    "platform": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Star_Carr_headdress.jpg/320px-Star_Carr_headdress.jpg",
    
    # Species photos
    "Birch": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Betula_pendula_001.jpg/220px-Betula_pendula_001.jpg",
    "Willow": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Salix_alba_Morton.jpg/220px-Salix_alba_Morton.jpg",
    "Alder": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Alnus_glutinosa_008.jpg/220px-Alnus_glutinosa_008.jpg",
    "Aspen": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Populus_tremula_-_trembling_aspen_-_aspen_-_52281825394.jpg/220px-Populus_tremula_-_trembling_aspen_-_aspen_-_52281825394.jpg",
    "Hazel": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Corylus_avellana_-_hazel_-_hazelaar_-_Fumay.jpg/220px-Corylus_avellana_-_hazel_-_hazelaar_-_Fumay.jpg",
    "Reed": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phragmites_australis_Cam.jpg/220px-Phragmites_australis_Cam.jpg",
    "Nettle": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Urtica_dioica_-_stinging_nettle_-_Grote_brandnetel.jpg/220px-Urtica_dioica_-_stinging_nettle_-_Grote_brandnetel.jpg",
    "Sedge": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Carex_acutiformis_-_lesser_pond_sedge_-_moeraszegge_-_01.jpg/220px-Carex_acutiformis_-_lesser_pond_sedge_-_moeraszegge_-_01.jpg",
    "Red_Deer": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cervus_elaphus_Luc_Viatour_6.jpg/220px-Cervus_elaphus_Luc_Viatour_6.jpg",
    "Elk": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Moose_superior.jpg/220px-Moose_superior.jpg",
    "Roe_Deer": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Capreolus_capreolus_2_-_Bournemouth.jpg/220px-Capreolus_capreolus_2_-_Bournemouth.jpg",
    "Aurochs": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Ur-painting.jpg/220px-Ur-painting.jpg",
    "Wild_Boar": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Sus_scrofa_1_-_Whipsnade_Zoo.jpg/220px-Sus_scrofa_1_-_Whipsnade_Zoo.jpg",
    "Beaver": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Beaver_-_Castor_fiber_-_01.jpg/220px-Beaver_-_Castor_fiber_-_01.jpg",
    "Wolf": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Eurasian_wolf_2.jpg/220px-Eurasian_wolf_2.jpg",
    "Brown_Bear": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Kamchatka_Brown_Bear_near_Dvuhyurtochnoe_on_2015-07-23.jpg/220px-Kamchatka_Brown_Bear_near_Dvuhyurtochnoe_on_2015-07-23.jpg",
    "Pike": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Esox_lucius_ZOO_1.jpg/220px-Esox_lucius_ZOO_1.jpg",
    "Waterfowl": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Anas_platyrhynchos_male_female_quadrat.jpg/220px-Anas_platyrhynchos_male_female_quadrat.jpg",
}

# Known working fallback URLs (verified to exist)
FALLBACKS = {
    "deep_water": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Crater_Lake_winter_pano2.jpg/320px-Crater_Lake_winter_pano2.jpg",
    "shallow_water": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/SwampCypress.jpg/320px-SwampCypress.jpg",
    "wetland": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Marsh_Meadows.jpg/320px-Marsh_Meadows.jpg",
    "mixed_woodland": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camaldoli_28-04-08_f13b.jpg/320px-Camaldoli_28-04-08_f13b.jpg",
    "grassland": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/GrasslandVeld.jpg/320px-GrasslandVeld.jpg",
    "platform": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Star_Carr_Antler_Mask.jpg/220px-Star_Carr_Antler_Mask.jpg",
}


def test_url(name, url):
    """Test if a URL returns 200 OK."""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            print(f"✓ {name}: OK")
            return True
        else:
            print(f"✗ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {name}: {str(e)[:50]}")
        return False


def main():
    print("Testing all photo URLs...\n")
    
    broken = []
    for name, url in URLS_TO_TEST.items():
        if not test_url(name, url):
            broken.append(name)
    
    print(f"\n--- Results ---")
    print(f"Working: {len(URLS_TO_TEST) - len(broken)}")
    print(f"Broken: {len(broken)}")
    
    if broken:
        print(f"\nBroken URLs: {', '.join(broken)}")
        print("\nSuggested fixes:")
        for name in broken:
            if name in FALLBACKS:
                print(f"  {name}: {FALLBACKS[name]}")
            else:
                print(f"  {name}: Search Wikimedia Commons for replacement")


if __name__ == "__main__":
    main()
