import logging

from .models import Cart as CartModel
from .models import CartItem, Product

logger = logging.getLogger(__name__)


def _get_or_create_cart(request):
    """
    Return the Cart DB row for this request.
    - Logged-in user  → look up by user (create if missing)
    - Anonymous user  → look up by guest_token cookie (create if missing)
    """
    if request.user.is_authenticated:
        cart, _ = CartModel.objects.get_or_create(user=request.user)
        return cart

    guest_token = getattr(request, 'guest_token', None)
    if not guest_token:
        logger.warning("guest_token missing on request — cart will not persist")
        return CartModel()  # unsaved, in-memory only

    cart, _ = CartModel.objects.get_or_create(guest_token=guest_token)
    return cart


def merge_guest_cart(user, guest_token):
    """
    Call this after a guest logs in or completes signup.
    Moves all items from the guest cart into the user's cart, then deletes
    the guest cart. Quantities are summed for items that exist in both.
    """
    if not guest_token:
        return
    try:
        guest_cart = CartModel.objects.get(guest_token=guest_token)
    except CartModel.DoesNotExist:
        return

    user_cart, _ = CartModel.objects.get_or_create(user=user)

    for guest_item in guest_cart.items.select_related('product').all():
        user_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=guest_item.product,
            defaults={'quantity': guest_item.quantity},
        )
        if not created:
            user_item.quantity += guest_item.quantity
            user_item.save(update_fields=['quantity'])

    guest_cart.delete()


class Cart:
    """
    Thin wrapper around the DB Cart model that mirrors the old session-cart API
    so views.py needs zero changes.
    """

    def __init__(self, request):
        self._cart = _get_or_create_cart(request)

    def add(self, product, qty=1):
        if not self._cart.pk:
            return
        item, created = CartItem.objects.get_or_create(
            cart=self._cart,
            product=product,
            defaults={'quantity': qty},
        )
        if not created:
            item.quantity += qty
            item.save(update_fields=['quantity'])

    def remove(self, product_id):
        if not self._cart.pk:
            return
        CartItem.objects.filter(cart=self._cart, product_id=product_id).delete()

    def update(self, product_id, qty):
        if not self._cart.pk:
            return
        if qty <= 0:
            self.remove(product_id)
        else:
            CartItem.objects.filter(
                cart=self._cart, product_id=product_id
            ).update(quantity=qty)

    def clear(self):
        if not self._cart.pk:
            return
        self._cart.items.all().delete()

    @property
    def count(self):
        if not self._cart.pk:
            return 0
        return sum(item.quantity for item in self._cart.items.all())

    @property
    def total(self):
        if not self._cart.pk:
            from decimal import Decimal
            return Decimal('0')
        return self._cart.total

    def get_items(self):
        if not self._cart.pk:
            return []
        items = []
        for item in self._cart.items.select_related('product').all():
            items.append({
                'product': item.product,
                'qty': item.quantity,
                'price': item.product.price,
                'subtotal': item.subtotal,
            })
        return items
