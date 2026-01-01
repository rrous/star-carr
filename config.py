# Star Carr Mesolithic Scholar Simulator - Configuration

# Grid configuration
GRID_COLS = 200
GRID_ROWS = 250
CELL_SIZE_M = 10  # meters per cell
ORIGIN_E = 502500  # British National Grid easting
ORIGIN_N = 484500  # British National Grid northing

# Player spawn (platform location)
SPAWN_X = 20
SPAWN_Y = 42

# Visibility radius in cells (30m = 3 cells)
VISIBILITY_RADIUS = 3

# Species density (fraction of cells with notable species)
SPECIES_DENSITY = 0.3

# Terrain types
TERRAIN_TYPES = {
    0: {"name": "deep_water", "color": "#1e3a8a", "description": "Deep lake water, dark and cold", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Aerial_View_of_Lake_Bled.jpg/320px-Aerial_View_of_Lake_Bled.jpg"},
    1: {"name": "shallow_water", "color": "#3b82f6", "description": "Shallow lake margins, wading depth", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Swamp_lake_margins.jpg/320px-Swamp_lake_margins.jpg"},
    2: {"name": "reed_bed", "color": "#a3e635", "description": "Dense stands of tall reeds", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Phragmites_australis_-_reed_bed.jpg/320px-Phragmites_australis_-_reed_bed.jpg"},
    3: {"name": "wetland", "color": "#84cc16", "description": "Marshy ground with sedges and rushes", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Wetland_-_geograph.org.uk_-_1265382.jpg/320px-Wetland_-_geograph.org.uk_-_1265382.jpg"},
    4: {"name": "carr_woodland", "color": "#65a30d", "description": "Wet woodland of willow and alder", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Carr_woodland_-_geograph.org.uk_-_1257615.jpg/320px-Carr_woodland_-_geograph.org.uk_-_1257615.jpg"},
    5: {"name": "birch_woodland", "color": "#16a34a", "description": "Open birch-dominated forest", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Birch_forest_in_Russia.jpg/320px-Birch_forest_in_Russia.jpg"},
    6: {"name": "mixed_woodland", "color": "#15803d", "description": "Dense mixed deciduous woodland", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Mixed_forest_in_autumn.jpg/320px-Mixed_forest_in_autumn.jpg"},
    7: {"name": "grassland", "color": "#86efac", "description": "Open grassy clearings", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Grassland_in_England.jpg/320px-Grassland_in_England.jpg"},
    8: {"name": "platform", "color": "#92400e", "description": "Star Carr wooden platform - occupation site", "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Star_Carr_wooden_platform.jpg/320px-Star_Carr_wooden_platform.jpg"},
}

# Species database - ALL WITH PHOTO URLs
SPECIES_DATABASE = {
    1: {
        "id": 1,
        "latin_name": "Betula spp.",
        "common_name": "Birch",
        "category": "tree",
        "visual": "Slender trees with distinctive white papery bark marked by dark horizontal lines. Delicate branches carry small triangular leaves with serrated edges, now bright green in spring growth.",
        "tactile": "Bark peels in thin papery layers, smooth and cool to touch. Twigs are thin and flexible.",
        "smell": "Fresh, slightly sweet scent from new leaves. Bark has faint wintergreen aroma when scratched.",
        "sound": "Leaves rustle softly in breeze. Small birds frequent the branches.",
        "habitat": "Dominant in drier woodland areas, pioneer species colonizing open ground.",
        "season_note": "Spring catkins releasing pollen. Sap rising - can be tapped for sweet drink.",
        "uses": "Bark for containers, tar production, tinder. Wood for tools, firewood. Sap drinkable.",
        "abundance": "very_common",
        "terrain_preference": [5, 6, 7],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Betula_pendula_001.jpg/220px-Betula_pendula_001.jpg"
    },
    2: {
        "id": 2,
        "latin_name": "Salix spp.",
        "common_name": "Willow",
        "category": "tree",
        "visual": "Graceful trees with long, narrow silver-green leaves. Flexible branches hang toward water. Multiple stems often grow from base.",
        "tactile": "Bark is rough and deeply furrowed on old trees. Young shoots remarkably flexible, bending without breaking.",
        "smell": "Crushed leaves release fresh, slightly bitter green scent.",
        "sound": "Branches creak and sway. Favored by warblers whose song fills the carr.",
        "habitat": "Edges of water, wet ground, carr woodland. Roots stabilize riverbanks.",
        "season_note": "Fuzzy catkins appearing. New shoots sprouting vigorously.",
        "uses": "Flexible stems for basketry, fish traps, shelter frames. Bark contains pain-relieving compounds.",
        "abundance": "common",
        "terrain_preference": [3, 4],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Salix_alba_Morton.jpg/220px-Salix_alba_Morton.jpg"
    },
    3: {
        "id": 3,
        "latin_name": "Alnus glutinosa",
        "common_name": "Alder",
        "category": "tree",
        "visual": "Medium tree with dark fissured bark. Rounded leaves with notched tips. Small woody cones persist from last year alongside new catkins.",
        "tactile": "Bark rough and corky. Cut wood turns from white to orange-red when exposed to air.",
        "smell": "Damp, earthy scent. Crushed leaves slightly sticky.",
        "sound": "Home to many birds. Woodpeckers often drum on trunks.",
        "habitat": "Waterlogged ground, stream banks, carr woodland. Roots fix nitrogen.",
        "season_note": "Purple-red catkins extending. Last year's cones still releasing seeds.",
        "uses": "Wood resists rot underwater - ideal for platforms, posts. Good charcoal for smelting.",
        "abundance": "common",
        "terrain_preference": [3, 4],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Alnus_glutinosa_008.jpg/220px-Alnus_glutinosa_008.jpg"
    },
    4: {
        "id": 4,
        "latin_name": "Populus tremula",
        "common_name": "Aspen",
        "category": "tree",
        "visual": "Tall straight trunk with smooth pale gray-green bark. Round leaves on flattened stalks that allow constant movement.",
        "tactile": "Bark smooth on young trees, becoming rough with diamond-shaped marks with age.",
        "smell": "Mild, clean scent. Buds are resinous and fragrant.",
        "sound": "Distinctive constant rustling even in lightest breeze - 'trembling' leaves give its name.",
        "habitat": "Woodland edges, clearings, colonizes disturbed ground quickly via root suckers.",
        "season_note": "Fuzzy catkins before leaves emerge. Suckers sprouting from roots.",
        "uses": "Light soft wood for carving, paddles. Inner bark edible in emergency.",
        "abundance": "occasional",
        "terrain_preference": [5, 6, 7],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Populus_tremula_-_trembling_aspen_-_aspen_-_52281825394.jpg/220px-Populus_tremula_-_trembling_aspen_-_aspen_-_52281825394.jpg"
    },
    5: {
        "id": 5,
        "latin_name": "Corylus avellana",
        "common_name": "Hazel",
        "category": "shrub",
        "visual": "Multi-stemmed shrub or small tree. Broad, soft leaves with pointed tips and toothed edges. Straight poles grow from base.",
        "tactile": "Leaves softly hairy. Young stems smooth and flexible. Nuts (in autumn) have hard shells.",
        "smell": "Fresh green leafy scent. Catkin pollen has dusty smell.",
        "sound": "Nuthatches and jays frequent for nuts. Dormice rustle in branches.",
        "habitat": "Woodland understory, edges, hedgerows. Tolerates shade well.",
        "season_note": "Long yellow catkins ('lamb's tails') releasing pollen. Tiny red female flowers visible.",
        "uses": "Nuts highly nutritious (autumn). Straight rods for tools, traps, shelter frames. Excellent firewood.",
        "abundance": "common",
        "terrain_preference": [5, 6],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Corylus_avellana_-_hazel_-_hazelaar_-_Fumay.jpg/220px-Corylus_avellana_-_hazel_-_hazelaar_-_Fumay.jpg"
    },
    6: {
        "id": 6,
        "latin_name": "Phragmites australis",
        "common_name": "Common Reed",
        "category": "plant",
        "visual": "Tall grass-like stems reaching 2-3 meters. Dead tan stems from last year mixed with fresh green shoots. Feathery seed heads persist.",
        "tactile": "Stems hollow and rigid. Leaves have sharp edges that can cut skin. Roots form dense underwater mat.",
        "smell": "Fresh green smell mixed with slight decay from old stems. Damp organic scent.",
        "sound": "Dry stems rattle and creak in wind. Reed beds alive with bird calls - warblers, bitterns.",
        "habitat": "Shallow water margins, forming dense beds at lake edges.",
        "season_note": "New green shoots pushing through old stems. Reed warblers returning to nest.",
        "uses": "Stems for thatching, matting, arrow shafts. Roots edible. Dense beds shelter fish and fowl.",
        "abundance": "abundant",
        "terrain_preference": [2],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phragmites_australis_Cam.jpg/220px-Phragmites_australis_Cam.jpg"
    },
    7: {
        "id": 7,
        "latin_name": "Urtica dioica",
        "common_name": "Stinging Nettle",
        "category": "plant",
        "visual": "Dark green plants with heart-shaped serrated leaves covered in fine hairs. Grows in dense patches to waist height.",
        "tactile": "WARNING: Stinging hairs cause painful burning rash on contact. Handle only when dried or cooked.",
        "smell": "Pungent, green, slightly unpleasant when crushed.",
        "sound": "Buzzing of insects - many pollinators visit the flowers.",
        "habitat": "Disturbed ground, especially where humans or animals have enriched soil. Indicates occupation sites.",
        "season_note": "Young spring shoots are most tender for eating and fiber extraction.",
        "uses": "Young leaves edible when cooked (very nutritious). Stem fibers make strong cordage and cloth.",
        "abundance": "common",
        "terrain_preference": [7, 8],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Urtica_dioica_-_stinging_nettle_-_Grote_brandnetel.jpg/220px-Urtica_dioica_-_stinging_nettle_-_Grote_brandnetel.jpg"
    },
    8: {
        "id": 8,
        "latin_name": "Carex spp.",
        "common_name": "Sedge",
        "category": "plant",
        "visual": "Grass-like plants growing in dense tussocks. Triangular stems distinguish from true grasses. Various heights.",
        "tactile": "Stems triangular in cross-section ('sedges have edges'). Leaves can be sharp. Tough and fibrous.",
        "smell": "Clean, slightly sweet grass-like scent.",
        "sound": "Soft rustling. Many small birds shelter and nest in tussocks.",
        "habitat": "Wet ground, marshes, stream banks. Different species in different water depths.",
        "season_note": "Fresh growth emerging from tussock centers. Flower spikes developing.",
        "uses": "Leaves for weaving, cordage, thatching. Tussocks indicate firm(ish) ground in marshes.",
        "abundance": "abundant",
        "terrain_preference": [2, 3, 4],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Carex_acutiformis_-_lesser_pond_sedge_-_moeraszegge_-_01.jpg/220px-Carex_acutiformis_-_lesser_pond_sedge_-_moeraszegge_-_01.jpg"
    },
    10: {
        "id": 10,
        "latin_name": "Cervus elaphus",
        "common_name": "Red Deer",
        "category": "large_herbivore",
        "visual": "Large deer with rich reddish-brown coat. Stags carry impressive branching antlers. Pale rump patch. Calves spotted.",
        "tactile": "Tracks: Large cloven hoofprints, ~8cm long. Droppings cylindrical with pointed end.",
        "smell": "Musky scent, especially near wallows. Droppings have grassy odor.",
        "sound": "Barking alarm call. Calves bleat. Stags roar in autumn rut (not now in spring).",
        "habitat": "Woodland edges, clearings, browse in forest. Regular trails between feeding areas.",
        "season_note": "Hinds heavily pregnant or with newborn calves. Stags in bachelor groups, antlers growing.",
        "uses": "PRIMARY PREY: ~80kg meat per adult. Antler for tools, bone for needles/points, hide for clothing, sinew for thread.",
        "abundance": "common",
        "terrain_preference": [5, 6, 7],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cervus_elaphus_Luc_Viatour_6.jpg/220px-Cervus_elaphus_Luc_Viatour_6.jpg"
    },
    11: {
        "id": 11,
        "latin_name": "Alces alces",
        "common_name": "Elk (Moose)",
        "category": "large_herbivore",
        "visual": "MASSIVE deer, dark brown-black, humped shoulders, long legs. Overhanging muzzle. Males have broad palmate antlers.",
        "tactile": "Tracks: Very large cloven prints ~15cm, splayed in soft ground. Deep impressions in mud.",
        "smell": "Strong musky odor near feeding areas. Pungent urine scent marks territory.",
        "sound": "Usually silent. Occasional low grunt. Crashing through vegetation when disturbed.",
        "habitat": "Wetlands, lake margins, feeds on aquatic plants. Wades into water to feed.",
        "season_note": "Cows with young calves, very protective. Bulls' antlers beginning spring growth.",
        "uses": "Enormous meat yield ~200kg. Hide extremely thick and warm. Antler for large tools.",
        "abundance": "occasional",
        "terrain_preference": [2, 3, 4],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Moose_superior.jpg/220px-Moose_superior.jpg"
    },
    12: {
        "id": 12,
        "latin_name": "Capreolus capreolus",
        "common_name": "Roe Deer",
        "category": "large_herbivore",
        "visual": "Small elegant deer, reddish summer coat. White rump patch. Short antlers on bucks (3 points). Large dark eyes.",
        "tactile": "Tracks: Small neat cloven prints ~4cm. Droppings small, shiny black pellets.",
        "smell": "Bucks mark territory with scent glands - musky odor on rubbed saplings.",
        "sound": "Sharp barking alarm call, often repeated. Kids make high whistling contact call.",
        "habitat": "Dense woodland with understory. Secretive, uses cover. Territorial.",
        "season_note": "Does pregnant, will give birth in late spring. Bucks establishing territories.",
        "uses": "Smaller meat yield ~12kg but tender. Hide soft and supple for fine work.",
        "abundance": "common",
        "terrain_preference": [5, 6],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Capreolus_capreolus_2_-_Bournemouth.jpg/220px-Capreolus_capreolus_2_-_Bournemouth.jpg"
    },
    13: {
        "id": 13,
        "latin_name": "Bos primigenius",
        "common_name": "Aurochs",
        "category": "large_herbivore",
        "visual": "ENORMOUS wild cattle, standing 1.8m at shoulder. Bulls black with pale dorsal stripe, cows reddish-brown. Long forward-curving horns.",
        "tactile": "Tracks: Massive round hoofprints ~12cm. Dung in large flat pats. Rubbing posts on trees.",
        "smell": "Strong cattle smell. Dung attracts many flies. Bulls particularly pungent.",
        "sound": "Deep bellowing. Snorting when alarmed. Ground trembles when herd runs.",
        "habitat": "Open grassland, woodland clearings, wetland edges. Grazes and browses.",
        "season_note": "Calving season. Bulls aggressive. DANGEROUS - do not approach.",
        "uses": "Massive meat yield ~350kg but VERY DANGEROUS to hunt. Hide thick, horns for containers.",
        "abundance": "rare",
        "terrain_preference": [7, 3],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Ur-painting.jpg/220px-Ur-painting.jpg"
    },
    14: {
        "id": 14,
        "latin_name": "Sus scrofa",
        "common_name": "Wild Boar",
        "category": "large_herbivore",
        "visual": "Stocky pig with coarse dark bristly coat. Long snout, small eyes. Males have curved tusks. Piglets striped.",
        "tactile": "Tracks: Cloven hooves with dew claw marks behind ~6cm. Rooting churns up soil. Mud wallows.",
        "smell": "Strong pungent pig smell. Wallows smell of mud and musk. Rooted areas smell of earth.",
        "sound": "Grunting while feeding. Piglets squeal. Alarmed adults make loud 'woof' bark.",
        "habitat": "Woodland with undergrowth, especially oak/beech (in autumn). Wetland edges.",
        "season_note": "Sows with litters of striped piglets. Boars can be aggressive - give space.",
        "uses": "Good meat yield ~40kg, rich fat. Hide for leather. Tusks and bones for tools. DANGEROUS when cornered.",
        "abundance": "occasional",
        "terrain_preference": [4, 5, 6],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Sus_scrofa_1_-_Whipsnade_Zoo.jpg/220px-Sus_scrofa_1_-_Whipsnade_Zoo.jpg"
    },
    15: {
        "id": 15,
        "latin_name": "Castor fiber",
        "common_name": "European Beaver",
        "category": "medium_herbivore",
        "visual": "Large rodent with dense brown fur, broad flat scaly tail. Small ears, webbed hind feet. Mostly seen at dawn/dusk.",
        "tactile": "Signs: Distinctive tooth marks on felled trees, pointed stumps. Dams of sticks and mud. Lodge mounds.",
        "smell": "Castoreum scent marks near water - musky, strong. Lodges smell of wet wood and vegetation.",
        "sound": "Loud tail slap on water as alarm. Gnawing sounds at night. Kits whine.",
        "habitat": "Rivers, lake edges, ponds. Creates own habitat by damming. Needs woody vegetation nearby.",
        "season_note": "Kits born in lodge. Adults very active repairing winter damage. Territorial.",
        "uses": "Highly valued fur (waterproof). Castoreum for medicine/bait. Meat edible. Dam pools trap fish.",
        "abundance": "occasional",
        "terrain_preference": [1, 2, 4],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Beaver_-_Castor_fiber_-_01.jpg/220px-Beaver_-_Castor_fiber_-_01.jpg"
    },
    20: {
        "id": 20,
        "latin_name": "Canis lupus",
        "common_name": "Wolf",
        "category": "predator",
        "visual": "Large dog-like predator, grey-brown fur, bushy tail. Travels in packs. Yellow eyes, large paws.",
        "tactile": "Tracks: Large dog prints ~10cm but more elongated than domestic dog. Travel in single file.",
        "smell": "Musky canine scent at marking posts. Kills have distinctive wolf smell.",
        "sound": "Iconic howling, especially at dusk/dawn. Yipping, growling. Pups whine at den.",
        "habitat": "Wide-ranging across all terrain following prey. Dens in secluded spots.",
        "season_note": "Denning season - pups born. Pack centered on den. Adults hunting to feed young.",
        "uses": "Fur warm but spiritually significant. Competitor for deer. Potential THREAT to humans especially to children.",
        "abundance": "rare",
        "terrain_preference": [5, 6, 7],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Eurasian_wolf_2.jpg/220px-Eurasian_wolf_2.jpg"
    },
    21: {
        "id": 21,
        "latin_name": "Ursus arctos",
        "common_name": "Brown Bear",
        "category": "predator",
        "visual": "Massive predator, brown fur varying light to dark. Distinctive shoulder hump. Small rounded ears. Huge clawed paws.",
        "tactile": "Tracks: Huge prints showing five toes and claws, ~25cm. Claw marks high on trees. Large droppings with berry seeds/hair.",
        "smell": "Strong musky bear odor. Can detect carrion from miles away. Marked trees smell pungent.",
        "sound": "Usually silent. Woofing alarm. Roaring when aggressive. Cubs mewl and hum.",
        "habitat": "Woodland, forest edges. Needs large territory. Follows seasonal food sources.",
        "season_note": "MOST DANGEROUS NOW - emerging from hibernation, very hungry. Sows with cubs extremely aggressive.",
        "uses": "Fur highly prized. Fat rendered for many uses. EXTREMELY DANGEROUS - avoid at all costs.",
        "abundance": "very_rare",
        "terrain_preference": [5, 6],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Kamchatka_Brown_Bear_near_Dvuhyurtochnoe_on_2015-07-23.jpg/220px-Kamchatka_Brown_Bear_near_Dvuhyurtochnoe_on_2015-07-23.jpg"
    },
    30: {
        "id": 30,
        "latin_name": "Esox lucius",
        "common_name": "Pike",
        "category": "aquatic",
        "visual": "Large predatory fish, elongated body with green-gold mottling. Flattened snout full of sharp teeth. Lurks motionless, then strikes.",
        "tactile": "Slimy scales. Gill covers sharp-edged. Teeth will cut fingers - handle carefully!",
        "smell": "Fresh fish smell. Weedy/muddy scent in shallows where they lurk.",
        "sound": "Splash when striking prey at surface. Otherwise silent.",
        "habitat": "Lakes, slow rivers. Ambush predator hiding in weed beds and reed edges.",
        "season_note": "Post-spawning, hungry and active. Can be speared in shallows, especially at dawn.",
        "uses": "Good eating despite bones - ~2-5kg typical. Y-bones require careful preparation.",
        "abundance": "common",
        "terrain_preference": [1, 2],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Esox_lucius_ZOO_1.jpg/220px-Esox_lucius_ZOO_1.jpg"
    },
    31: {
        "id": 31,
        "latin_name": "Anas/Anser spp.",
        "common_name": "Waterfowl",
        "category": "aquatic",
        "visual": "Various ducks and geese. Mallards common - male with green head. Geese larger, grey-brown. Swimming, dabbling, grazing on banks.",
        "tactile": "Webbed footprints in mud. Nests hidden in reeds lined with down. Eggs smooth, various sizes.",
        "smell": "Slight musty bird smell. Nesting areas smell of droppings and feathers.",
        "sound": "Quacking ducks, honking geese. Wing whistles in flight. Alarm calls when disturbed.",
        "habitat": "Lake surface, reed beds (nesting), grassy banks (grazing geese).",
        "season_note": "NESTING NOW - eggs available. Be careful not to disturb too many nests. Ducklings and goslings appearing.",
        "uses": "Meat, eggs, feathers (fletching, bedding), down (insulation). Can be netted, trapped, or arrows.",
        "abundance": "abundant",
        "terrain_preference": [1, 2, 3],
        "photo_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Anas_platyrhynchos_male_female_quadrat.jpg/220px-Anas_platyrhynchos_male_female_quadrat.jpg"
    }
}

# Create lookup by terrain for species distribution
def get_species_for_terrain(terrain_id):
    """Return list of species IDs that can appear in given terrain."""
    suitable = []
    for species_id, data in SPECIES_DATABASE.items():
        if terrain_id in data["terrain_preference"]:
            suitable.append(species_id)
    return suitable
