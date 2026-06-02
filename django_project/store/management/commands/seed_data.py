"""Populate the DB with the full catalog of categories and products."""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product

CATEGORIES = [
    {"slug": "tws-earbuds",  "name": "TWS Earbuds",
     "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600"},
    {"slug": "headphones",   "name": "Headphones",
     "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600"},
    {"slug": "neckbands",    "name": "Neckbands",
     "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600"},
    {"slug": "speakers",     "name": "Bluetooth Speakers",
     "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600"},
    {"slug": "accessories",  "name": "Accessories",
     "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600"},
]

PRODUCTS = [
    # ── TWS Earbuds ───────────────────────────────────────────────────────────
    {
        "name": "Buds 3 Pro", "category": "tws-earbuds",
        "price": 999,  "original_price": 1499, "rating": 4.4, "reviews_count": 3277, "bestseller": True,
        "feature": "Wireless | 40mm Sound Drivers",
        "description": "Experience pure, immersive audio with the Buds 3 Pro. Featuring active noise cancellation, 30-hour battery life, and wireless charging support — crafted for the way you live.",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Buds Elite", "category": "tws-earbuds",
        "price": 1199, "original_price": 1799, "rating": 4.5, "reviews_count": 2893, "bestseller": False,
        "feature": "Premium 10mm Drivers | 28hr Battery",
        "description": "Precision-tuned 10mm dynamic drivers deliver bass-rich sound with crystal-clear highs. The Buds Elite are built for music lovers who demand more.",
        "image_url": "https://images.unsplash.com/photo-1607087365600-e7bf50d0b226?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Buds Mini", "category": "tws-earbuds",
        "price": 699,  "original_price": 999,  "rating": 4.2, "reviews_count": 1567, "bestseller": False,
        "feature": "Compact Design | IPX5 Water Resistant",
        "description": "Small but mighty. The Buds Mini pack surprising audio quality into an ultra-compact form factor with an IPX5 water-resistant build perfect for workouts.",
        "image_url": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "SoundPods Ultra", "category": "tws-earbuds",
        "price": 1599, "original_price": 2499, "rating": 4.7, "reviews_count": 1892, "bestseller": True,
        "feature": "Hybrid ANC | Spatial Audio | 36hr Total",
        "description": "Flagship-level audio in a truly wireless form. Hybrid Active Noise Cancellation, Spatial Audio, and a custom-tuned 12mm driver make this the ultimate earbud.",
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Sport Pro Earbuds", "category": "tws-earbuds",
        "price": 899,  "original_price": 1299, "rating": 4.3, "reviews_count": 1134, "bestseller": False,
        "feature": "IPX7 | Ear-Wing Fit | Ambient Sound Mode",
        "description": "Engineered for athletes. The Sport Pro Earbuds stay locked in place during intense workouts with an IPX7 waterproof rating and ergonomic ear-wing design.",
        "image_url": "https://images.unsplash.com/photo-1548921441-89c8bd86ffb7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },

    # ── Headphones ────────────────────────────────────────────────────────────
    {
        "name": "AudioMax X1", "category": "headphones",
        "price": 1299, "original_price": 1999, "rating": 4.6, "reviews_count": 2156, "bestseller": True,
        "feature": "50mm Neodymium Drivers | Foldable",
        "description": "Studio-quality sound meets everyday comfort. The AudioMax X1 features large 50mm neodymium drivers and plush memory foam cushions for hours of fatigue-free listening.",
        "image_url": "https://images.unsplash.com/photo-1713618651165-a3cf7f85506c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Studio Pro Headphones", "category": "headphones",
        "price": 1899, "original_price": 2999, "rating": 4.8, "reviews_count": 4127, "bestseller": True,
        "feature": "Hi-Res Audio Certified | 40hr Battery",
        "description": "Hi-Res Audio certified for studio-grade reproduction. Adaptive ANC with 40-hour battery life and premium anodised aluminium build — these headphones mean business.",
        "image_url": "https://images.unsplash.com/photo-1505751171710-1f6d0ace5a85?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Pro Gaming Headset", "category": "headphones",
        "price": 1799, "original_price": 2799, "rating": 4.6, "reviews_count": 987,  "bestseller": False,
        "feature": "7.1 Surround | Detachable Mic | RGB",
        "description": "Dominate every session with 7.1 virtual surround sound, a precision detachable mic, and customisable RGB lighting. Compatible with PC, PS5, Xbox, and Switch.",
        "image_url": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Foldable DJ Headphones", "category": "headphones",
        "price": 2499, "original_price": 3999, "rating": 4.7, "reviews_count": 743,  "bestseller": True,
        "feature": "DJ-Grade | 90° Swivel Cups | Wired/BT",
        "description": "Professional DJ headphones with 90° swivel ear cups, a frequency response of 5–35,000 Hz, and the flexibility of wired or Bluetooth connectivity.",
        "image_url": "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },

    # ── Neckbands ─────────────────────────────────────────────────────────────
    {
        "name": "Flex Sport Neckband", "category": "neckbands",
        "price": 799,  "original_price": 1299, "rating": 4.3, "reviews_count": 1845, "bestseller": False,
        "feature": "Magnetic Earbuds | 20hr Battery",
        "description": "Snap-together magnetic earbuds and a flexible neck cable that stays in place during runs and gym sessions. 20-hour battery keeps the music going all day.",
        "image_url": "https://images.unsplash.com/photo-1632247541401-3d4a8d516595?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Executive Neckband Pro", "category": "neckbands",
        "price": 999,  "original_price": 1599, "rating": 4.5, "reviews_count": 1102, "bestseller": False,
        "feature": "ENC Mic | Voice Assistant | 24hr Battery",
        "description": "Designed for professionals on the go. Environmental Noise Cancellation mic delivers crystal-clear call quality, and Google Assistant / Siri activate at a single tap.",
        "image_url": "https://images.unsplash.com/photo-1558089687-f282ffcbc0b6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },

    # ── Speakers ──────────────────────────────────────────────────────────────
    {
        "name": "BoomBox Pro", "category": "speakers",
        "price": 1599, "original_price": 2499, "rating": 4.7, "reviews_count": 3521, "bestseller": True,
        "feature": "360° Surround Sound | 20W Output",
        "description": "Fill any room with powerful, room-shaking bass and 360° surround sound. 20W RMS output, IPX6 waterproof, 18-hour playtime — the ultimate party companion.",
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "MiniBlast Speaker", "category": "speakers",
        "price": 899,  "original_price": 1399, "rating": 4.4, "reviews_count": 2234, "bestseller": False,
        "feature": "Compact & Portable | 10W | IPX5",
        "description": "Big sound from a palm-sized speaker. The MiniBlast delivers 10W of crisp audio, connects via Bluetooth 5.3, and its IPX5 rating means it survives splashes and rain.",
        "image_url": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Party Cube Speaker", "category": "speakers",
        "price": 2199, "original_price": 3499, "rating": 4.6, "reviews_count": 876,  "bestseller": True,
        "feature": "40W Peak | LED Light Show | TWS Pair",
        "description": "Turn any gathering into a festival. 40W peak power output with a built-in LED light show synced to the beat. Pair two Party Cubes wirelessly for true stereo.",
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },

    # ── Accessories ───────────────────────────────────────────────────────────
    {
        "name": "Premium Braided Cable", "category": "accessories",
        "price": 199,  "original_price": 399,  "rating": 4.1, "reviews_count": 654,  "bestseller": False,
        "feature": "3.5mm | Nylon Braided | Gold-Plated",
        "description": "Gold-plated 3.5mm connectors and a tangle-resistant nylon braid ensure pristine audio signal and long-lasting durability. 1.2 m length with mic support.",
        "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Wireless Charging Stand", "category": "accessories",
        "price": 799,  "original_price": 1199, "rating": 4.3, "reviews_count": 423,  "bestseller": False,
        "feature": "15W Fast Charge | Dual-Device | LED",
        "description": "Charge your earbuds case and phone simultaneously with 15W fast wireless charging. Slim upright stand with a soft anti-slip base and ambient LED status indicator.",
        "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
    {
        "name": "Carrying Pouch Set", "category": "accessories",
        "price": 299,  "original_price": 499,  "rating": 4.2, "reviews_count": 317,  "bestseller": False,
        "feature": "Hard Shell + Mesh Bag | Scratch-Proof",
        "description": "A set of two protective cases — a hard EVA shell for on-the-go protection and a soft mesh bag for light storage at home. Fits most earbuds and neckbands.",
        "image_url": "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=600",
    },
]


class Command(BaseCommand):
    help = 'Seed the database with initial categories and products.'

    def handle(self, *args, **options):
        cat_map = {}
        for data in CATEGORIES:
            obj, created = Category.objects.update_or_create(
                slug=data['slug'],
                defaults={'name': data['name'], 'image_url': data['image_url']},
            )
            cat_map[data['slug']] = obj
            self.stdout.write(f"  {'Created' if created else 'Updated'} category: {obj.name}")

        for data in PRODUCTS:
            slug = slugify(data['name'])
            obj, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'name':          data['name'],
                    'category':      cat_map[data['category']],
                    'price':         data['price'],
                    'original_price':data['original_price'],
                    'image_url':     data['image_url'],
                    'description':   data.get('description', ''),
                    'feature':       data.get('feature', ''),
                    'rating':        data['rating'],
                    'reviews_count': data['reviews_count'],
                    'bestseller':    data['bestseller'],
                    'stock':         100,
                    'is_active':     True,
                },
            )
            self.stdout.write(f"  {'Created' if created else 'Updated'} product: {obj.name}")

        self.stdout.write(self.style.SUCCESS(
            f'Seed complete — {len(CATEGORIES)} categories, {len(PRODUCTS)} products.'
        ))
