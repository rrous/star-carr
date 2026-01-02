#!/usr/bin/env python3
"""
Star Carr Image Downloader - Direct URLs
Uses working Wikimedia Commons thumbnail URLs.
"""

import os
import requests
import random
from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    os.system("pip install pillow --break-system-packages -q")
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static", "images")
IMAGE_SIZE = (400, 300)
TIMEOUT = 15

# Direct working URLs from Wikimedia Commons (same format as config.py)
# Pattern: /thumb/{hash}/{filename}/{width}px-{filename}

SPECIES_URLS = {
    # Trees (4) - from config.py
    "birch": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Betula_pendula_001.jpg/220px-Betula_pendula_001.jpg",
    "willow": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Salix_alba_Morton.jpg/220px-Salix_alba_Morton.jpg",
    "alder": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Alnus_glutinosa_008.jpg/220px-Alnus_glutinosa_008.jpg",
    "aspen": None,  # no photo in config.py
    # Shrubs & Plants (4)
    "hazel": None,  # no photo in config.py
    "reed": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phragmites_australis_Cam.jpg/220px-Phragmites_australis_Cam.jpg",
    "nettle": None,  # no photo in config.py
    "sedge": None,  # no photo in config.py
    # Large Herbivores (5)
    "red_deer": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cervus_elaphus_Luc_Viatour_6.jpg/220px-Cervus_elaphus_Luc_Viatour_6.jpg",
    "elk": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Moose_superior.jpg/220px-Moose_superior.jpg",
    "roe_deer": None,  # no photo in config.py
    "aurochs": None,  # no photo in config.py
    "wild_boar": None,  # no photo in config.py
    # Medium Herbivores (1)
    "beaver": None,  # no photo in config.py
    # Predators (2)
    "wolf": None,  # no photo in config.py
    "brown_bear": None,  # no photo in config.py
    # Aquatic (2)
    "pike": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Esox_lucius_ZOO_1.jpg/220px-Esox_lucius_ZOO_1.jpg",
    "waterfowl": None,  # no photo in config.py
}

# Terrain URLs - seasonal variants where available
TERRAIN_URLS = {
    "deep_water": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Langvatnet%2C_Byrkjelo.jpg/400px-Langvatnet%2C_Byrkjelo.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Bluewater_Lake_NM.jpg/400px-Bluewater_Lake_NM.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Lake_mapourika_NZ.jpeg/400px-Lake_mapourika_NZ.jpeg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Frozen_Lake_Baikal.jpg/400px-Frozen_Lake_Baikal.jpg",
    },
    "shallow_water": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wetland_Georgia.jpg/400px-Wetland_Georgia.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Bluewater_Lake_NM.jpg/400px-Bluewater_Lake_NM.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Lake_mapourika_NZ.jpeg/400px-Lake_mapourika_NZ.jpeg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Frozen_Lake_Baikal.jpg/400px-Frozen_Lake_Baikal.jpg",
    },
    "reed_bed": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phragmites_australis_Cam.jpg/400px-Phragmites_australis_Cam.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phragmites_australis_Cam.jpg/400px-Phragmites_australis_Cam.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Schilf_im_Herbst.jpg/400px-Schilf_im_Herbst.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Schnee_auf_Schilf.jpg/400px-Schnee_auf_Schilf.jpg",
    },
    "wetland": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wetland_Georgia.jpg/400px-Wetland_Georgia.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wetland_Georgia.jpg/400px-Wetland_Georgia.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wetland_Georgia.jpg/400px-Wetland_Georgia.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wetland_Georgia.jpg/400px-Wetland_Georgia.jpg",
    },
    "carr_woodland": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg/400px-Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg/400px-Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg/400px-Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg/400px-Alder_carr%2C_Clatto_Country_Park_-_geograph.org.uk_-_161109.jpg",
    },
    "birch_woodland": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Birkenwaelder_01.jpg/400px-Birkenwaelder_01.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Birkenwaelder_01.jpg/400px-Birkenwaelder_01.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Autumn_Birch_Forest.jpg/400px-Autumn_Birch_Forest.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Birch_forest_in_winter.JPG/400px-Birch_forest_in_winter.JPG",
    },
    "mixed_woodland": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grib_skov.jpg/400px-Grib_skov.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grib_skov.jpg/400px-Grib_skov.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Autumn_deciduous_forest.jpg/400px-Autumn_deciduous_forest.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Bare_deciduous_trees_in_winter.jpg/400px-Bare_deciduous_trees_in_winter.jpg",
    },
    "grassland": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Alpine_meadow.jpg/400px-Alpine_meadow.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Alpine_meadow.jpg/400px-Alpine_meadow.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Alpine_meadow.jpg/400px-Alpine_meadow.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Frost_on_grass.JPG/400px-Frost_on_grass.JPG",
    },
    "platform": {
        "spring": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Sweet_Track.jpg/400px-Sweet_Track.jpg",
        "summer": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Sweet_Track.jpg/400px-Sweet_Track.jpg",
        "autumn": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Sweet_Track.jpg/400px-Sweet_Track.jpg",
        "winter": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Sweet_Track.jpg/400px-Sweet_Track.jpg",
    },
}

COLORS = {
    "deep_water": "#1e3a8a", "shallow_water": "#3b82f6", "reed_bed": "#a3e635",
    "wetland": "#84cc16", "carr_woodland": "#65a30d", "birch_woodland": "#16a34a",
    "mixed_woodland": "#15803d", "grassland": "#86efac", "platform": "#92400e",
    "birch": "#d4edda", "willow": "#c3e6cb", "alder": "#a8d5a2", "aspen": "#b8e0b8",
    "hazel": "#8b7355", "reed": "#9acd32", "nettle": "#228b22", "sedge": "#6b8e23",
    "red_deer": "#8b4513", "elk": "#5d4037", "roe_deer": "#a0522d", "aurochs": "#3e2723",
    "wild_boar": "#4a4a4a", "beaver": "#6d4c41", "wolf": "#607d8b", "brown_bear": "#5d4037",
    "pike": "#4682b4", "waterfowl": "#5f9ea0",
}

SEASONS = ["spring", "summer", "autumn", "winter"]


def create_placeholder(name: str, season: str = None) -> Image.Image:
    """Create gradient placeholder."""
    color = COLORS.get(name, "#888888")
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    
    if season:
        adj = {"spring": (20, 40, 10), "summer": (30, 20, -10),
               "autumn": (40, -10, -30), "winter": (-20, -10, 30)}[season]
        r, g, b = [max(0, min(255, c + a)) for c, a in zip((r, g, b), adj)]
    
    img = Image.new('RGB', IMAGE_SIZE)
    draw = ImageDraw.Draw(img)
    for y in range(IMAGE_SIZE[1]):
        f = 1.0 - (y / IMAGE_SIZE[1]) * 0.4
        draw.line([(0, y), (IMAGE_SIZE[0], y)], fill=(int(r*f), int(g*f), int(b*f)))
    
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    draw = ImageDraw.Draw(img)
    
    label = name.replace("_", " ").title()
    if season:
        label += f"\n({season})"
    
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    x, y = (IMAGE_SIZE[0] - bbox[2]) / 2, (IMAGE_SIZE[1] - bbox[3]) / 2
    draw.text((x+1, y+1), label, font=font, fill="#000", align="center")
    draw.text((x, y), label, font=font, fill="#FFF", align="center")
    
    return img


def download(url: str, filepath: str) -> bool:
    """Download image from URL."""
    try:
        headers = {'User-Agent': 'StarCarrBot/1.0'}
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200 and len(resp.content) > 1000:
            img = Image.open(BytesIO(resp.content)).convert('RGB')
            # Crop to aspect ratio
            ratio = img.width / img.height
            target = IMAGE_SIZE[0] / IMAGE_SIZE[1]
            if ratio > target:
                w = int(img.height * target)
                img = img.crop(((img.width - w) // 2, 0, (img.width + w) // 2, img.height))
            else:
                h = int(img.width / target)
                img = img.crop((0, (img.height - h) // 2, img.width, (img.height + h) // 2))
            img = img.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
            img.save(filepath, 'JPEG', quality=85)
            return True
    except Exception as e:
        print(f"    Error: {e}")
    return False


def main():
    print("="*50)
    print("STAR CARR IMAGE DOWNLOADER")
    print("="*50)
    
    # Create dirs
    for d in ["terrain", "species"]:
        os.makedirs(os.path.join(STATIC_DIR, d), exist_ok=True)
    
    downloaded, placeholders = 0, 0
    
    # Species
    print("\nSPECIES:")
    for name, url in SPECIES_URLS.items():
        filepath = os.path.join(STATIC_DIR, "species", f"{name}.jpg")
        print(f"  {name}...", end=" ")
        if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
            print("exists")
            continue
        if url and download(url, filepath):
            print("OK")
            downloaded += 1
        else:
            create_placeholder(name).save(filepath, 'JPEG')
            print("placeholder")
            placeholders += 1
    
    # Terrain
    print("\nTERRAIN:")
    for terrain, seasons in TERRAIN_URLS.items():
        for season, url in seasons.items():
            filepath = os.path.join(STATIC_DIR, "terrain", f"{terrain}_{season}.jpg")
            print(f"  {terrain}_{season}...", end=" ")
            if os.path.exists(filepath) and os.path.getsize(filepath) > 5000:
                print("exists")
                continue
            if download(url, filepath):
                print("OK")
                downloaded += 1
            else:
                create_placeholder(terrain, season).save(filepath, 'JPEG')
                print("placeholder")
                placeholders += 1
    
    print(f"\nDone: {downloaded} downloaded, {placeholders} placeholders")
    print(f"Output: {STATIC_DIR}")


if __name__ == "__main__":
    main()
