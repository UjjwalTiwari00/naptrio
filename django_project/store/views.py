import hashlib
import hmac
import json
import logging

import razorpay
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .models import Category, Order, OrderItem, Product, SiteSettings

logger = logging.getLogger(__name__)

HERO_SLIDES = [
    "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=1600",
    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=1600",
    "https://images.unsplash.com/photo-1484704849700-f032a568e944?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=1600",
    "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=1600",
    "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=1600",
]

WHY_FEATURES = [
    {"icon": "music",        "title": "Premium Sound",   "desc": "Experience crystal clear audio quality"},
    {"icon": "zap",          "title": "Fast Charging",   "desc": "Quick charge for all-day listening"},
    {"icon": "droplets",     "title": "Water Resistant", "desc": "IPX5 rated for sweat and splash proof"},
    {"icon": "shield-check", "title": "1 Year Warranty", "desc": "Protected with comprehensive warranty"},
    {"icon": "truck",        "title": "Free Shipping",   "desc": "Free delivery on all orders"},
]


def _base_context(request, **extra):
    try:
        categories = list(Category.objects.all())
    except Exception:
        logger.exception("Failed to load categories for nav")
        categories = []
    ctx = {
        'nav_categories': categories,
        'promo_text': 'Diwali Deals from Nov 5 – Nov 10 2026',
        'active_slug': extra.pop('active_slug', None),
    }
    ctx.update(extra)
    return ctx


def _razorpay_client():
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '') or ''
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '') or ''
    if not key_id or not key_secret:
        raise ValueError("Razorpay keys are not configured in settings.")
    return razorpay.Client(auth=(key_id, key_secret))


def _send_order_emails(order):
    """Send confirmation emails — never raises; all failures are logged."""
    try:
        items_text = '\n'.join(
            f"  • {item.product.name} × {item.quantity} = ₹{item.subtotal}"
            for item in order.items.select_related('product').all()
        )
    except Exception:
        logger.exception("Failed to build items text for order #%s", order.id)
        items_text = "(could not load items)"

    # Email to customer
    try:
        send_mail(
            subject=f'Order Confirmed — Naptrio #{order.id}',
            message=(
                f"Hi {order.name},\n\n"
                f"Thank you for your order! Here's a summary:\n\n"
                f"Order ID : #{order.id}\n"
                f"Items    :\n{items_text}\n"
                f"Total    : ₹{order.total}\n\n"
                f"Shipping to: {order.address}\n\n"
                f"We'll notify you when your order ships.\n\n"
                f"— Team Naptrio"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send confirmation email to customer for order #%s", order.id)

    # Email to admin
    try:
        admin_email = SiteSettings.get().admin_notification_email
        send_mail(
            subject=f'New Order #{order.id} — ₹{order.total} — {order.name}',
            message=(
                f"New order received!\n\n"
                f"Order ID  : #{order.id}\n"
                f"Customer  : {order.name}\n"
                f"Email     : {order.email}\n"
                f"Phone     : {order.phone}\n"
                f"Address   : {order.address}\n\n"
                f"Items:\n{items_text}\n\n"
                f"Total: ₹{order.total}\n\n"
                f"Manage: {getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}"
                f"/admin/store/order/{order.id}/change/"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send admin alert for order #%s", order.id)


# ── Storefront pages ──────────────────────────────────────────────────────────

def home(request):
    try:
        products = list(Product.objects.filter(is_active=True).select_related('category'))
        bestsellers = [p for p in products if p.bestseller]
    except Exception:
        logger.exception("Failed to load products for home page")
        products, bestsellers = [], []

    try:
        categories_grid = Category.objects.all()
    except Exception:
        logger.exception("Failed to load categories grid for home page")
        categories_grid = []

    ctx = _base_context(
        request,
        slides=HERO_SLIDES,
        latest_products=products[:8],
        bestsellers=bestsellers,
        categories_grid=categories_grid,
        why_features=WHY_FEATURES,
    )
    return render(request, 'store/home.html', ctx)


def category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    try:
        products = Product.objects.filter(category=cat, is_active=True)
    except Exception:
        logger.exception("Failed to load products for category %s", slug)
        products = []
    ctx = _base_context(request, category=cat, products=products, active_slug=slug)
    return render(request, 'store/category.html', ctx)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        related = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product_id)[:4]
    except Exception:
        logger.exception("Failed to load related products for product #%s", product_id)
        related = []
    ctx = _base_context(request, product=product, related_products=related)
    return render(request, 'store/product_detail.html', ctx)


def about(request):
    return render(request, 'store/about.html', _base_context(request))


def contact(request):
    return render(request, 'store/contact.html', _base_context(request))


def corporate(request):
    return render(request, 'store/corporate.html', _base_context(request))


# ── Cart ──────────────────────────────────────────────────────────────────────

def cart_detail(request):
    cart = Cart(request)
    try:
        cart_items = cart.get_items()
        cart_total = cart.total
    except Exception:
        logger.exception("Failed to load cart items")
        cart_items, cart_total = [], 0
    ctx = _base_context(request, cart_items=cart_items, cart_total=cart_total)
    return render(request, 'store/cart.html', ctx)


@require_POST
def cart_add(request):
    try:
        product_id = request.POST.get('product_id')
        qty = max(1, int(request.POST.get('qty', 1)))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid quantity'}, status=400)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        cart = Cart(request)
        cart.add(product, qty)
        return JsonResponse({'ok': True, 'count': cart.count, 'name': product.name})
    except Exception:
        logger.exception("Failed to add product #%s to cart", product_id)
        return JsonResponse({'ok': False, 'error': 'Could not add item to cart'}, status=500)


@require_POST
def cart_remove(request):
    try:
        product_id = request.POST.get('product_id')
        cart = Cart(request)
        cart.remove(product_id)
        return JsonResponse({'ok': True, 'count': cart.count, 'total': str(cart.total)})
    except Exception:
        logger.exception("Failed to remove product from cart")
        return JsonResponse({'ok': False, 'error': 'Could not remove item'}, status=500)


@require_POST
def cart_update(request):
    try:
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('qty', 1))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid quantity'}, status=400)
    try:
        cart = Cart(request)
        cart.update(product_id, qty)
        item_subtotal = None
        for item in cart.get_items():
            if str(item['product'].id) == str(product_id):
                item_subtotal = str(item['subtotal'])
                break
        return JsonResponse({
            'ok': True,
            'count': cart.count,
            'total': str(cart.total),
            'item_subtotal': item_subtotal,
        })
    except Exception:
        logger.exception("Failed to update cart for product #%s", product_id)
        return JsonResponse({'ok': False, 'error': 'Could not update cart'}, status=500)


# ── Checkout ──────────────────────────────────────────────────────────────────

def checkout(request):
    cart = Cart(request)
    try:
        if not cart.count:
            return redirect('store:cart')
    except Exception:
        return redirect('store:cart')

    customer = None
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except Exception:
            pass

    prefill = {}
    if customer:
        try:
            prefill = {
                'name':    request.user.get_full_name() or request.user.username,
                'email':   request.user.email,
                'phone':   customer.phone,
                'address': customer.full_address,
            }
        except Exception:
            logger.exception("Failed to build prefill for user #%s", request.user.id)

    try:
        cart_items = cart.get_items()
        cart_total = cart.total
    except Exception:
        logger.exception("Failed to load cart items for checkout")
        cart_items, cart_total = [], 0

    ctx = _base_context(
        request,
        cart_items=cart_items,
        cart_total=cart_total,
        prefill=prefill,
        razorpay_key_id=getattr(settings, 'RAZORPAY_KEY_ID', ''),
    )
    return render(request, 'store/checkout.html', ctx)


@require_POST
def create_razorpay_order(request):
    """Creates a Razorpay order — returns id + amount to frontend."""
    try:
        cart = Cart(request)
        if not cart.count:
            return JsonResponse({'ok': False, 'error': 'Your cart is empty.'}, status=400)

        amount_paise = int(cart.total * 100)
        if amount_paise <= 0:
            return JsonResponse({'ok': False, 'error': 'Order amount must be greater than zero.'}, status=400)

        client = _razorpay_client()
        rz_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
        })
        return JsonResponse({'ok': True, 'razorpay_order_id': rz_order['id'], 'amount': amount_paise})

    except ValueError as e:
        # Razorpay keys not configured
        logger.error("Razorpay not configured: %s", e)
        return JsonResponse({'ok': False, 'error': 'Payment gateway is not configured. Please contact support.'}, status=503)
    except razorpay.errors.BadRequestError as e:
        logger.exception("Razorpay bad request while creating order")
        return JsonResponse({'ok': False, 'error': 'Could not initiate payment. Please try again.'}, status=400)
    except Exception:
        logger.exception("Unexpected error creating Razorpay order")
        return JsonResponse({'ok': False, 'error': 'Payment service is unavailable. Please try again shortly.'}, status=503)


@require_POST
def verify_payment(request):
    """Verifies Razorpay signature, saves order to DB, sends emails."""
    # Parse body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'Invalid request.'}, status=400)

    razorpay_order_id   = (data.get('razorpay_order_id') or '').strip()
    razorpay_payment_id = (data.get('razorpay_payment_id') or '').strip()
    razorpay_signature  = (data.get('razorpay_signature') or '').strip()
    name    = (data.get('name') or '').strip()
    email   = (data.get('email') or '').strip()
    phone   = (data.get('phone') or '').strip()
    address = (data.get('address') or '').strip()

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, name, email, phone, address]):
        return JsonResponse({'ok': False, 'error': 'Missing required fields.'}, status=400)

    # Verify HMAC-SHA256 signature
    try:
        key_secret = (getattr(settings, 'RAZORPAY_KEY_SECRET', '') or '').encode()
        if not key_secret:
            raise ValueError("RAZORPAY_KEY_SECRET is not configured.")
        expected = hmac.new(
            key_secret,
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, razorpay_signature):
            logger.warning(
                "Payment signature mismatch — order_id=%s payment_id=%s",
                razorpay_order_id, razorpay_payment_id,
            )
            return JsonResponse({'ok': False, 'error': 'Payment verification failed. Please contact support.'}, status=400)
    except ValueError as e:
        logger.error("Razorpay key secret issue: %s", e)
        return JsonResponse({'ok': False, 'error': 'Payment configuration error. Please contact support.'}, status=503)
    except Exception:
        logger.exception("Unexpected error during signature verification")
        return JsonResponse({'ok': False, 'error': 'Could not verify payment. Please contact support.'}, status=500)

    # Signature valid — save order to DB
    try:
        cart = Cart(request)
        customer = None
        if request.user.is_authenticated:
            try:
                customer = request.user.customer
            except Exception:
                pass

        order = Order.objects.create(
            name=name, email=email, phone=phone, address=address,
            session_key=request.session.session_key or '',
            customer=customer,
        )
        for item in cart.get_items():
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['qty'],
                price=item['price'],
            )
        order.recalculate_total()
        cart.clear()
    except Exception:
        # CRITICAL: payment succeeded but order save failed — log everything for manual recovery
        logger.critical(
            "PAYMENT RECEIVED BUT ORDER SAVE FAILED — "
            "razorpay_order_id=%s razorpay_payment_id=%s customer_email=%s amount_approx=check_razorpay",
            razorpay_order_id, razorpay_payment_id, email,
        )
        return JsonResponse({
            'ok': False,
            'error': (
                'Your payment was received but we had a technical issue saving your order. '
                'Please contact support with your payment ID: ' + razorpay_payment_id
            ),
        }, status=500)

    # Send emails — never let this block the success response
    try:
        _send_order_emails(order)
    except Exception:
        logger.exception("Email sending failed for order #%s — order is saved, continuing", order.id)

    return JsonResponse({'ok': True, 'order_id': order.id})


def order_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    ctx = _base_context(request, order=order)
    return render(request, 'store/order_confirm.html', ctx)


# ── Misc ──────────────────────────────────────────────────────────────────────

@require_POST
def subscribe(request):
    email = (request.POST.get('email') or '').strip()
    if not email:
        return JsonResponse({'ok': False, 'error': 'Email required.'}, status=400)
    return JsonResponse({'ok': True, 'message': 'Subscribed — welcome to the Naptrio family!'})
