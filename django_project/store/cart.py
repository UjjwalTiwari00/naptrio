import logging
from decimal import Decimal, InvalidOperation

from .models import Product

logger = logging.getLogger(__name__)


class Cart:
    SESSION_KEY = 'naptrio_cart'

    def __init__(self, request):
        self.session = request.session
        # setdefault writes the key into the session if absent, so self.cart is
        # always a direct reference to the dict inside the session — not a
        # detached copy. Without this, session.get(key, {}) returns a floating
        # dict that is never actually stored, so cart.add() mutates an object
        # the session knows nothing about and nothing ever persists.
        raw = self.session.setdefault(self.SESSION_KEY, {})
        if not isinstance(raw, dict):
            logger.warning("Cart session data was corrupted, resetting.")
            self.session[self.SESSION_KEY] = {}
            raw = self.session[self.SESSION_KEY]
        self.cart = raw

    def _save(self):
        self.session.modified = True

    def add(self, product, qty=1):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {
                'qty': 0,
                'price': str(product.price),
                'name': product.name,
                'image': product.image_url,
            }
        self.cart[pid]['qty'] += qty
        self._save()

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)
        self._save()

    def update(self, product_id, qty):
        pid = str(product_id)
        if pid in self.cart:
            if qty <= 0:
                self.remove(product_id)
            else:
                self.cart[pid]['qty'] = qty
                self._save()

    def clear(self):
        self.session.pop(self.SESSION_KEY, None)
        self.session.modified = True

    @property
    def count(self):
        total = 0
        for item in self.cart.values():
            try:
                total += int(item.get('qty', 0))
            except (TypeError, ValueError):
                pass
        return total

    @property
    def total(self):
        result = Decimal('0')
        for item in self.cart.values():
            try:
                result += Decimal(str(item['price'])) * int(item['qty'])
            except (KeyError, TypeError, ValueError, InvalidOperation):
                pass
        return result

    def get_items(self):
        if not self.cart:
            return []
        try:
            products = {str(p.id): p for p in Product.objects.filter(id__in=self.cart.keys())}
        except Exception:
            logger.exception("Failed to fetch products for cart")
            return []

        items = []
        for pid, data in self.cart.items():
            product = products.get(pid)
            if not product:
                continue
            try:
                qty = int(data['qty'])
                price = Decimal(str(data['price']))
                items.append({
                    'product': product,
                    'qty': qty,
                    'price': price,
                    'subtotal': price * qty,
                })
            except (KeyError, TypeError, ValueError, InvalidOperation):
                logger.warning("Skipping corrupted cart entry for product id=%s", pid)
        return items
