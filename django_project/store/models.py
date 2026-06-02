from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image_url = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    feature = models.CharField(max_length=200, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    reviews_count = models.PositiveIntegerField(default=0)
    bestseller = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def savings(self):
        return self.original_price - self.price

    @property
    def discount_percent(self):
        if self.original_price > 0:
            return int((self.original_price - self.price) / self.original_price * 100)
        return 0


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_address(self):
        parts = [self.address, self.city, self.state, self.pincode]
        return ', '.join(p for p in parts if p)

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders'
    )
    session_key = models.CharField(max_length=40, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.name}"

    def recalculate_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=['total'])

    @property
    def status_color(self):
        return {
            'pending':   'yellow',
            'confirmed': 'blue',
            'shipped':   'purple',
            'delivered': 'green',
            'cancelled': 'red',
        }.get(self.status, 'gray')

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class SiteSettings(models.Model):
    """Singleton — only one row (pk=1). Edit via Django admin."""
    admin_notification_email = models.EmailField(
        help_text="All new-order alerts go to this address."
    )

    # SMTP configuration — managed from admin, no redeployment needed
    smtp_host = models.CharField(
        max_length=255, default='smtp.gmail.com',
        help_text="SMTP server hostname, e.g. smtp.gmail.com"
    )
    smtp_port = models.PositiveIntegerField(
        default=587,
        help_text="SMTP port (587 for TLS, 465 for SSL, 25 for plain)"
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        help_text="Use STARTTLS (port 587). Disable for SSL (port 465)."
    )
    smtp_use_ssl = models.BooleanField(
        default=False,
        help_text="Use SSL (port 465). Mutually exclusive with TLS."
    )
    smtp_user = models.CharField(
        max_length=255, blank=True,
        help_text="Email address used to authenticate with the SMTP server."
    )
    smtp_password = models.CharField(
        max_length=255, blank=True,
        help_text="App password / SMTP password. For Gmail use an App Password."
    )
    from_email = models.EmailField(
        blank=True,
        help_text="'From' address shown to recipients. Defaults to smtp_user if blank."
    )

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={'admin_notification_email': 'imujjwaltiwari@gmail.com'},
        )
        return obj

    # Razorpay configuration — managed from admin, no redeployment needed
    razorpay_key_id = models.CharField(
        max_length=255, blank=True,
        help_text="Razorpay Key ID — starts with rzp_test_ or rzp_live_"
    )
    razorpay_key_secret = models.CharField(
        max_length=255, blank=True,
        help_text="Razorpay Key Secret. Keep this confidential."
    )

    @property
    def effective_from_email(self):
        return self.from_email or self.smtp_user


class EmailOTP(models.Model):
    """Stores a pending email-verification OTP for new signups."""
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP for {self.email}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
