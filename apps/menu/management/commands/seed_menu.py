"""
Management command to seed a restaurant's menu with standard Indian restaurant items.

Usage:
    python manage.py seed_menu --restaurant <slug-or-id>
    python manage.py seed_menu --restaurant my-restaurant --clear   # wipe existing menu first
"""

from django.core.management.base import BaseCommand, CommandError
from apps.tenants.models import Restaurant
from apps.menu.models import MenuCategory, MenuItem


# ---------------------------------------------------------------------------
# Menu data: (name, price, is_veg, description)
# Prices are in INR — sensible mid-range defaults, easy to edit.
# ---------------------------------------------------------------------------
MENU_DATA = [
    {
        "category": "Starters — Veg",
        "order": 1,
        "items": [
            ("Samosa (2 pcs)",         60,   True,  "Crispy pastry filled with spiced potato and peas"),
            ("Aloo Tikki",             80,   True,  "Pan-fried spiced potato patties served with chutneys"),
            ("Hara Bhara Kabab",       120,  True,  "Spinach, peas and paneer patties grilled in tandoor"),
            ("Veg Seekh Kabab",        140,  True,  "Spiced vegetable mince skewers grilled in tandoor"),
            ("Paneer Tikka",           180,  True,  "Marinated cottage cheese cubes grilled in tandoor"),
            ("Dahi Puri",              90,   True,  "Crisp puris filled with yoghurt, sev and chutneys"),
            ("Papdi Chaat",            100,  True,  "Crispy wafers topped with potatoes, yoghurt and chutneys"),
            ("Veg Spring Roll",        110,  True,  "Crispy rolls stuffed with stir-fried vegetables"),
            ("Paneer Pakora",          150,  True,  "Cottage cheese fritters in spiced gram flour batter"),
        ],
    },
    {
        "category": "Starters — Non Veg",
        "order": 2,
        "items": [
            ("Chicken 65",             180,  False, "Deep-fried spicy chicken — South Indian classic"),
            ("Chicken Tikka",          220,  False, "Marinated boneless chicken grilled in tandoor"),
            ("Tandoori Chicken (Half)", 280, False, "Classic half chicken marinated in yoghurt and spices"),
            ("Chicken Malai Tikka",    240,  False, "Creamy, mildly spiced boneless chicken tikka"),
            ("Mutton Seekh Kabab",     280,  False, "Minced mutton skewers grilled in tandoor"),
            ("Fish Tikka",             260,  False, "Marinated fish cubes grilled in tandoor"),
            ("Prawn Koliwada",         300,  False, "Spicy batter-fried prawns in Maharashtrian style"),
            ("Chilli Chicken (Dry)",   200,  False, "Indo-Chinese style crispy chicken tossed with peppers"),
        ],
    },
    {
        "category": "Soups",
        "order": 3,
        "items": [
            ("Tomato Soup",            90,   True,  "Classic creamy tomato soup"),
            ("Sweet Corn Soup (Veg)",  100,  True,  "Creamy sweet corn soup with vegetables"),
            ("Manchow Soup (Veg)",     100,  True,  "Spicy Indo-Chinese soup with crispy noodles"),
            ("Hot & Sour Soup (Veg)",  100,  True,  "Tangy and spicy vegetable soup"),
            ("Chicken Sweet Corn Soup",120,  False, "Classic sweet corn soup with shredded chicken"),
            ("Manchow Soup (Chicken)", 130,  False, "Spicy Indo-Chinese chicken soup with crispy noodles"),
        ],
    },
    {
        "category": "Breads",
        "order": 4,
        "items": [
            ("Tandoori Roti",          30,   True,  "Whole wheat bread baked in tandoor"),
            ("Butter Roti",            35,   True,  "Tandoori roti finished with butter"),
            ("Butter Naan",            50,   True,  "Soft leavened bread baked in tandoor with butter"),
            ("Garlic Naan",            60,   True,  "Naan topped with garlic and coriander"),
            ("Cheese Naan",            80,   True,  "Naan stuffed with melted cheese"),
            ("Lachha Paratha",         60,   True,  "Layered whole wheat bread baked in tandoor"),
            ("Stuffed Kulcha",         80,   True,  "Leavened bread stuffed with spiced potato"),
            ("Missi Roti",             40,   True,  "Spiced gram flour and wheat bread from tandoor"),
            ("Puri (2 pcs)",           40,   True,  "Deep-fried whole wheat puffed bread"),
        ],
    },
    {
        "category": "Rice & Biryani",
        "order": 5,
        "items": [
            ("Steamed Rice",           80,   True,  "Plain steamed basmati rice"),
            ("Jeera Rice",             100,  True,  "Basmati rice tempered with cumin"),
            ("Veg Pulao",              130,  True,  "Fragrant basmati rice cooked with mixed vegetables"),
            ("Veg Biryani",            180,  True,  "Aromatic basmati rice with spiced vegetables — dum style"),
            ("Paneer Biryani",         220,  True,  "Dum biryani with cottage cheese and whole spices"),
            ("Egg Biryani",            200,  False, "Aromatic biryani with boiled eggs"),
            ("Chicken Biryani",        260,  False, "Classic dum biryani with tender chicken"),
            ("Mutton Biryani",         320,  False, "Slow-cooked dum biryani with tender mutton"),
            ("Prawn Biryani",          340,  False, "Fragrant dum biryani with spiced prawns"),
        ],
    },
    {
        "category": "Dal",
        "order": 6,
        "items": [
            ("Dal Tadka",              140,  True,  "Yellow lentils tempered with ghee and spices"),
            ("Dal Makhani",            160,  True,  "Slow-cooked black lentils in butter and cream"),
            ("Dal Fry",                140,  True,  "Mixed lentils fried with onion, tomato and spices"),
            ("Panchmel Dal",           150,  True,  "Five-lentil blend from Rajasthani cuisine"),
            ("Palak Dal",              150,  True,  "Lentils cooked with fresh spinach and spices"),
        ],
    },
    {
        "category": "Veg Curries & Mains",
        "order": 7,
        "items": [
            ("Aloo Jeera",             130,  True,  "Potato cubes tossed with cumin and spices"),
            ("Aloo Gobi",              140,  True,  "Potato and cauliflower dry curry"),
            ("Aloo Matar",             140,  True,  "Potato and green peas in tomato gravy"),
            ("Baingan Bharta",         150,  True,  "Smoked aubergine mash with spices"),
            ("Bhindi Masala",          150,  True,  "Stir-fried okra with onions and spices"),
            ("Mix Veg",                160,  True,  "Seasonal vegetables in a mildly spiced gravy"),
            ("Matar Mushroom",         170,  True,  "Green peas and mushrooms in onion-tomato gravy"),
            ("Kadai Veg",              180,  True,  "Mixed vegetables in a robust kadai masala"),
            ("Veg Kolhapuri",          190,  True,  "Spicy mixed vegetables in Kolhapuri masala"),
            ("Veg Kofta Curry",        200,  True,  "Fried vegetable dumplings in creamy tomato gravy"),
        ],
    },
    {
        "category": "Paneer Dishes",
        "order": 8,
        "items": [
            ("Paneer Butter Masala",   220,  True,  "Cottage cheese in rich, creamy tomato gravy"),
            ("Palak Paneer",           210,  True,  "Cottage cheese in smooth spinach gravy"),
            ("Shahi Paneer",           230,  True,  "Cottage cheese in a royal cashew-cream gravy"),
            ("Kadai Paneer",           220,  True,  "Cottage cheese with capsicum in kadai masala"),
            ("Paneer Tikka Masala",    240,  True,  "Grilled paneer tikka in a tangy masala gravy"),
            ("Matar Paneer",           200,  True,  "Cottage cheese and green peas in tomato gravy"),
            ("Paneer Lababdar",        230,  True,  "Cottage cheese in a smoky, buttery tomato gravy"),
            ("Paneer Do Pyaza",        220,  True,  "Cottage cheese with double the onions"),
        ],
    },
    {
        "category": "Non-Veg Curries & Mains",
        "order": 9,
        "items": [
            ("Butter Chicken",         280,  False, "Tender chicken in a rich, creamy tomato gravy"),
            ("Chicken Tikka Masala",   290,  False, "Grilled chicken tikka in a tangy masala gravy"),
            ("Kadai Chicken",          270,  False, "Chicken with capsicum in kadai masala"),
            ("Chicken Curry",          240,  False, "Classic home-style chicken curry"),
            ("Chicken Korma",          280,  False, "Mild chicken curry in a cashew and yoghurt gravy"),
            ("Chicken Do Pyaza",       260,  False, "Chicken cooked with double the onions"),
            ("Mutton Rogan Josh",      360,  False, "Slow-cooked mutton in aromatic Kashmiri gravy"),
            ("Mutton Curry",           340,  False, "Classic mutton curry with whole spices"),
            ("Mutton Korma",           360,  False, "Tender mutton in a rich cashew and yoghurt gravy"),
            ("Fish Curry",             300,  False, "Fish in a tangy, coastal-style gravy"),
            ("Prawn Masala",           360,  False, "Prawns in a spicy onion-tomato masala"),
        ],
    },
    {
        "category": "Indo-Chinese",
        "order": 10,
        "items": [
            ("Veg Fried Rice",         160,  True,  "Wok-tossed basmati rice with vegetables"),
            ("Paneer Fried Rice",      190,  True,  "Wok-tossed rice with cottage cheese"),
            ("Egg Fried Rice",         170,  False, "Wok-tossed rice with scrambled eggs"),
            ("Chicken Fried Rice",     200,  False, "Wok-tossed rice with chicken"),
            ("Veg Hakka Noodles",      160,  True,  "Stir-fried noodles with vegetables"),
            ("Chicken Hakka Noodles",  200,  False, "Stir-fried noodles with chicken"),
            ("Veg Schezwan Noodles",   170,  True,  "Noodles tossed in spicy Schezwan sauce"),
            ("Gobi Manchurian (Dry)",  160,  True,  "Crispy cauliflower tossed in Manchurian sauce"),
            ("Gobi Manchurian (Gravy)",170,  True,  "Cauliflower in Indo-Chinese Manchurian gravy"),
            ("Paneer Manchurian",      190,  True,  "Crispy paneer in tangy Manchurian sauce"),
            ("Chicken Manchurian",     210,  False, "Crispy chicken in tangy Manchurian sauce"),
            ("Veg Schezwan Rice",      170,  True,  "Fried rice tossed in spicy Schezwan sauce"),
        ],
    },
    {
        "category": "Desserts",
        "order": 11,
        "items": [
            ("Gulab Jamun (2 pcs)",    80,   True,  "Soft milk-solid dumplings soaked in rose syrup"),
            ("Rasgulla (2 pcs)",       80,   True,  "Soft cottage cheese balls in light sugar syrup"),
            ("Gajar Halwa",            120,  True,  "Slow-cooked carrot pudding with ghee and dry fruits"),
            ("Kheer",                  100,  True,  "Creamy rice pudding with cardamom and saffron"),
            ("Malai Kulfi",            100,  True,  "Traditional Indian ice cream — malai flavour"),
            ("Kesar Kulfi",            110,  True,  "Traditional Indian ice cream — saffron and pistachio"),
            ("Mango Kulfi",            110,  True,  "Traditional Indian ice cream — Alphonso mango"),
            ("Brownie with Ice Cream", 150,  True,  "Warm chocolate brownie served with vanilla ice cream"),
        ],
    },
    {
        "category": "Beverages",
        "order": 12,
        "items": [
            ("Sweet Lassi",            80,   True,  "Chilled blended yoghurt drink — sweet"),
            ("Salted Lassi",           70,   True,  "Chilled blended yoghurt drink — salted"),
            ("Mango Lassi",            100,  True,  "Chilled yoghurt drink with fresh mango pulp"),
            ("Rose Lassi",             90,   True,  "Yoghurt drink flavoured with rose syrup"),
            ("Masala Chaas",           60,   True,  "Spiced buttermilk with cumin and coriander"),
            ("Fresh Lime Soda",        70,   True,  "Fresh lime with soda — sweet, salted or mixed"),
            ("Cold Coffee",            110,  True,  "Chilled blended coffee with milk"),
            ("Fresh Juice (Seasonal)", 90,   True,  "Freshly pressed seasonal fruit juice"),
            ("Masala Chai",            40,   True,  "Spiced Indian milk tea"),
            ("Mineral Water (500ml)",  30,   True,  "Packaged mineral water"),
            ("Soft Drink (Can)",       50,   True,  "Chilled soft drink — Coke, Pepsi or Sprite"),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed an Indian restaurant's menu with standard categories and items"

    def add_arguments(self, parser):
        parser.add_argument(
            "--restaurant",
            required=True,
            help="Restaurant slug or numeric ID",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing menu before seeding",
        )

    def handle(self, *args, **options):
        identifier = options["restaurant"]

        # Resolve restaurant by slug or pk
        try:
            if identifier.isdigit():
                restaurant = Restaurant.objects.get(pk=int(identifier))
            else:
                restaurant = Restaurant.objects.get(slug=identifier)
        except Restaurant.DoesNotExist:
            raise CommandError(f"Restaurant '{identifier}' not found.")

        self.stdout.write(f"Seeding menu for: {restaurant.name}")

        if options["clear"]:
            deleted_items, _ = MenuItem.objects.filter(restaurant=restaurant).delete()
            deleted_cats, _ = MenuCategory.objects.filter(restaurant=restaurant).delete()
            self.stdout.write(
                self.style.WARNING(f"  Cleared {deleted_cats} categories and {deleted_items} items.")
            )

        total_cats = 0
        total_items = 0
        skipped = 0

        for block in MENU_DATA:
            cat, cat_created = MenuCategory.objects.get_or_create(
                restaurant=restaurant,
                name=block["category"],
                defaults={"display_order": block["order"], "is_active": True},
            )
            if cat_created:
                total_cats += 1
                self.stdout.write(f"  + Category: {cat.name}")

            for (name, price, is_veg, description) in block["items"]:
                _, item_created = MenuItem.objects.get_or_create(
                    restaurant=restaurant,
                    name=name,
                    defaults={
                        "category": cat,
                        "price": price,
                        "is_veg": is_veg,
                        "description": description,
                        "is_available": True,
                        "display_order": 0,
                    },
                )
                if item_created:
                    total_items += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Created {total_cats} categories, {total_items} items."
                + (f" Skipped {skipped} already-existing items." if skipped else "")
            )
        )
        self.stdout.write(f"Visit /dashboard/menu/ to view and edit the menu.")
