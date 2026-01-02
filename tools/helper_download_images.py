#!/usr/bin/env python3
"""
Download free images for Star Carr project.
Run once locally, then commit images to your repo.

Sources (all free, no attribution required):
- Pixabay: pixabay.com
- Pexels: pexels.com  
- Unsplash: unsplash.com (need to download manually)

INSTRUCTIONS:
1. Go to each URL below
2. Right-click image → Save As → static/images/[name].jpg
3. Update config.py photo_url to use "/static/images/[name].jpg"
"""

# Manual download links - visit these and save images:

TERRAIN_IMAGES = {
    "deep_water": "https://pixabay.com/photos/lake-water-blue-nature-mountains-1802337/",
    "shallow_water": "https://pixabay.com/photos/river-water-nature-landscape-5238241/",
    "reed_bed": "https://pixabay.com/photos/reed-plant-nature-grass-1913986/",
    "wetland": "https://pixabay.com/photos/marsh-swamp-wetland-nature-water-5464137/",
    "carr_woodland": "https://pixabay.com/photos/forest-swamp-trees-water-nature-5651894/",
    "birch_woodland": "https://pixabay.com/photos/birch-forest-trees-nature-white-1260899/",
    "mixed_woodland": "https://pixabay.com/photos/forest-trees-nature-autumn-fall-1868028/",
    "grassland": "https://pixabay.com/photos/meadow-grass-green-nature-summer-2184989/",
    "platform": "https://pixabay.com/photos/wood-planks-texture-wooden-brown-1866667/",
}

SPECIES_IMAGES = {
    "birch": "https://pixabay.com/photos/birch-tree-trunk-bark-white-1260859/",
    "willow": "https://pixabay.com/photos/willow-tree-weeping-willow-nature-3399830/",
    "alder": "https://pixabay.com/photos/alder-tree-deciduous-tree-leaves-5964115/",
    "aspen": "https://pixabay.com/photos/aspen-trees-autumn-fall-nature-1030850/",
    "hazel": "https://pixabay.com/photos/hazelnut-nut-fruit-brown-autumn-1707801/",
    "reed": "https://pixabay.com/photos/reed-grass-nature-plant-water-4655436/",
    "nettle": "https://pixabay.com/photos/stinging-nettle-urtica-nettle-plant-3431224/",
    "sedge": "https://pixabay.com/photos/grass-sedge-nature-green-meadow-5264566/",
    "red_deer": "https://pixabay.com/photos/deer-red-deer-antlers-nature-wild-1940369/",
    "elk": "https://pixabay.com/photos/moose-animal-wildlife-nature-wild-70254/",
    "roe_deer": "https://pixabay.com/photos/roe-deer-deer-animal-nature-wild-5765288/",
    "aurochs": "https://pixabay.com/photos/cattle-cow-animal-livestock-farm-2213644/",
    "wild_boar": "https://pixabay.com/photos/wild-boar-boar-pig-animal-wildlife-3382098/",
    "beaver": "https://pixabay.com/photos/beaver-animal-rodent-wildlife-7206019/",
    "wolf": "https://pixabay.com/photos/wolf-predator-canidae-canis-lupus-1336229/",
    "brown_bear": "https://pixabay.com/photos/bear-brown-bear-animal-wildlife-1245807/",
    "pike": "https://pixabay.com/photos/pike-fish-catch-fishing-angling-3377379/",
    "waterfowl": "https://pixabay.com/photos/mallard-duck-bird-water-fowl-2655664/",
}

print("="*60)
print("STAR CARR IMAGE DOWNLOAD GUIDE")
print("="*60)
print()
print("1. Create folder: static/images/")
print()
print("2. Visit each link below, download image, save as shown:")
print()

print("--- TERRAIN IMAGES ---")
for name, url in TERRAIN_IMAGES.items():
    print(f"  {name}.jpg  →  {url}")

print()
print("--- SPECIES IMAGES ---")
for name, url in SPECIES_IMAGES.items():
    print(f"  {name}.jpg  →  {url}")

print()
print("3. Update config.py to use local paths like:")
print('   "photo_url": "/static/images/red_deer.jpg"')
print()
print("4. Push to GitHub → Render redeploys with images")
print()
print("="*60)
