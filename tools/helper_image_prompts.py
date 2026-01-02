"""
STAR CARR IMAGE GENERATION GUIDE - Perchance.org
=================================================

SETUP:
1. Go to https://perchance.org/ai-text-to-image-generator
2. NO signup needed, unlimited free images
3. Paste prompt, click Generate
4. Right-click image → Save As → use filename shown below

FOLDER STRUCTURE:
static/images/
├── terrain/
│   ├── deep_water_spring.jpg
│   ├── deep_water_summer.jpg
│   ├── deep_water_autumn.jpg
│   ├── deep_water_winter.jpg
│   └── ... (9 terrains × 4 seasons = 36 images)
├── species/
│   ├── birch.jpg
│   ├── red_deer.jpg
│   └── ... (20 species)
└── resources/
    ├── antler.jpg
    ├── flint.jpg
    └── ... (optional)

PROMPTS BELOW - Copy/paste into Perchance.org:

TIP: Add "nature photography, 512x512" to end of each prompt for consistency
"""

# =============================================================================
# TERRAIN PROMPTS (9 terrains × 4 seasons = 36 images)
# =============================================================================

TERRAIN_PROMPTS = {
    "deep_water": {
        "base": "deep dark lake water, prehistoric Britain, {season}, natural photography, 9000 BCE landscape",
        "spring": "misty morning, ice melting, cold blue water",
        "summer": "clear deep blue water, reflections, sunny",
        "autumn": "dark water, fallen leaves floating, overcast",
        "winter": "partially frozen, ice forming, grey sky",
    },
    "shallow_water": {
        "base": "shallow lake margins, clear water, visible bottom, prehistoric Britain, {season}",
        "spring": "new reeds emerging, meltwater, bright",
        "summer": "warm shallows, aquatic plants, sunny",
        "autumn": "muddy edges, decaying vegetation",
        "winter": "frozen edges, thin ice, snow dusting",
    },
    "reed_bed": {
        "base": "dense phragmites reed bed, tall reeds, wetland, prehistoric Britain, {season}",
        "spring": "fresh green shoots among old tan stems",
        "summer": "lush green reeds, dense tall stands, feathery tops",
        "autumn": "golden brown reeds, seed heads, rustling",
        "winter": "dry tan reeds, snow covered, frozen base",
    },
    "wetland": {
        "base": "marshy wetland, sedges and rushes, boggy ground, prehistoric Britain, {season}",
        "spring": "waterlogged, fresh growth, tussocks",
        "summer": "lush green marsh, flowering plants, humid",
        "autumn": "golden sedges, standing water, misty",
        "winter": "frozen marsh, frost covered, brown vegetation",
    },
    "carr_woodland": {
        "base": "wet woodland, willow and alder trees, waterlogged forest floor, prehistoric Britain, {season}",
        "spring": "catkins, fresh leaves, flooded ground, birdsong",
        "summer": "dense green canopy, dappled light, humid",
        "autumn": "yellow willow leaves, fallen leaves in water",
        "winter": "bare branches, flooded, grey atmosphere",
    },
    "birch_woodland": {
        "base": "birch forest, white bark trees, open woodland, prehistoric Britain, {season}",
        "spring": "fresh green leaves, catkins, bright understory",
        "summer": "full canopy, dappled sunlight, ferns below",
        "autumn": "golden yellow leaves, white trunks contrast",
        "winter": "bare white trunks, snow, stark beauty",
    },
    "mixed_woodland": {
        "base": "dense mixed deciduous forest, oak hazel birch, prehistoric Britain, {season}",
        "spring": "bluebells, fresh leaves unfurling, green",
        "summer": "deep shade, full canopy, dense undergrowth",
        "autumn": "red orange yellow leaves, rich colors",
        "winter": "bare branches, leaf litter, grey light",
    },
    "grassland": {
        "base": "open grassland clearing, prehistoric Britain meadow, {season}",
        "spring": "fresh green grass, wildflowers emerging",
        "summer": "tall grass, wildflowers, buzzing insects, sunny",
        "autumn": "golden grass, seed heads, dry",
        "winter": "brown dormant grass, frost, open sky",
    },
    "platform": {
        "base": "mesolithic wooden platform, birch logs and branches, archaeological site, {season}",
        "spring": "wet wood, moss growing, lake edge camp",
        "summer": "weathered wood, dry, activity area",
        "autumn": "wet wood, fallen leaves on platform",
        "winter": "snow covered wooden platform, frozen",
    },
}

# =============================================================================
# SPECIES PROMPTS (20 species)
# =============================================================================

SPECIES_PROMPTS = {
    # Trees (4)
    "birch": "silver birch tree, white papery bark, Betula pendula, nature photography, prehistoric forest",
    "willow": "willow tree by water, Salix alba, flexible branches, wetland, nature photography",
    "alder": "alder tree, Alnus glutinosa, dark bark, cones and catkins, wet woodland",
    "aspen": "trembling aspen tree, Populus tremula, round leaves, white bark, forest edge",
    
    # Shrubs & Plants (4)
    "hazel": "hazel shrub, Corylus avellana, catkins, nuts, woodland understory",
    "reed": "common reed, Phragmites australis, tall feathery seed head, wetland",
    "nettle": "stinging nettle patch, Urtica dioica, dark green serrated leaves",
    "sedge": "sedge tussock, Carex species, triangular stems, wetland grass",
    
    # Large Herbivores (5)
    "red_deer": "red deer stag, Cervus elaphus, antlers, noble pose, prehistoric Britain, wildlife photography",
    "elk": "european elk moose, Alces alces, huge antlers, wetland, wildlife photography",
    "roe_deer": "roe deer, Capreolus capreolus, small elegant deer, forest edge, wildlife",
    "aurochs": "aurochs wild cattle, Bos primigenius, massive horns, prehistoric, illustration",
    "wild_boar": "wild boar, Sus scrofa, bristly coat, tusks, forest, wildlife photography",
    
    # Medium Herbivores (1)
    "beaver": "european beaver, Castor fiber, wet fur, by water, dam building, wildlife",
    
    # Predators (2)
    "wolf": "grey wolf, Canis lupus, piercing eyes, forest, wildlife photography",
    "brown_bear": "european brown bear, Ursus arctos, powerful, forest, wildlife photography",
    
    # Aquatic (2)
    "pike": "northern pike fish, Esox lucius, underwater, predatory, green gold pattern",
    "waterfowl": "mallard ducks, wetland, swimming, nature photography",
}

# =============================================================================
# RESOURCE PROMPTS (optional, 10 items)
# =============================================================================

RESOURCE_PROMPTS = {
    "antler": "red deer antler, shed antler on ground, bone tool material",
    "flint": "flint stone, knapped flint tool, prehistoric, sharp edges",
    "birch_bark": "birch bark roll, white papery bark, container material",
    "hide": "deer hide, animal skin, leather, stretched",
    "bone_needle": "prehistoric bone needle, fine point, sewing tool",
    "wooden_spear": "wooden spear, fire hardened tip, prehistoric weapon",
    "woven_basket": "prehistoric woven basket, willow weave, container",
    "fire_hearth": "prehistoric fire pit, stones, charcoal, ash, camp",
    "fish_trap": "woven fish trap, willow weave, prehistoric fishing",
    "cordage": "plant fiber cordage, twisted rope, nettle fiber",
}

# =============================================================================
# GENERATION SCRIPT - prints all prompts
# =============================================================================

def print_all_prompts():
    print("=" * 70)
    print("TERRAIN PROMPTS (copy each to Leonardo.ai)")
    print("=" * 70)
    
    count = 0
    for terrain, data in TERRAIN_PROMPTS.items():
        for season in ["spring", "summer", "autumn", "winter"]:
            prompt = f"{data['base'].replace('{season}', season)}, {data[season]}"
            filename = f"{terrain}_{season}.jpg"
            count += 1
            print(f"\n[{count}] {filename}")
            print(f"    {prompt}")
    
    print("\n" + "=" * 70)
    print("SPECIES PROMPTS")
    print("=" * 70)
    
    for name, prompt in SPECIES_PROMPTS.items():
        count += 1
        filename = f"{name}.jpg"
        print(f"\n[{count}] {filename}")
        print(f"    {prompt}")
    
    print("\n" + "=" * 70)
    print("RESOURCE PROMPTS (optional)")
    print("=" * 70)
    
    for name, prompt in RESOURCE_PROMPTS.items():
        count += 1
        filename = f"{name}.jpg"
        print(f"\n[{count}] {filename}")
        print(f"    {prompt}")
    
    print("\n" + "=" * 70)
    print(f"TOTAL: {count} images")
    print("=" * 70)


if __name__ == "__main__":
    print_all_prompts()
