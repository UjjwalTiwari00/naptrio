from django.contrib import admin
from .models import Cart, CartItem, Category, EmailOTP, Product, Customer, Order, OrderItem, SiteSettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'original_price', 'stock', 'bestseller', 'is_active']
    list_filter = ['category', 'bestseller', 'is_active']
    list_editable = ['price', 'stock', 'bestseller', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'status', 'total', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Notifications', {
            'fields': ('admin_notification_email',),
        }),
        ('SMTP Configuration', {
            'description': (
                'These credentials are used for all outgoing emails (OTP, order confirmations, etc.). '
                'For Gmail, set smtp_user to your Gmail address and smtp_password to a Gmail App Password '
                '(not your regular password). Changes take effect immediately without redeploying.'
            ),
            'fields': (
                'smtp_host', 'smtp_port',
                'smtp_use_tls', 'smtp_use_ssl',
                'smtp_user', 'smtp_password',
                'from_email',
            ),
        }),
        ('Razorpay Payment Gateway', {
            'description': (
                'Get your keys from dashboard.razorpay.com → Settings → API Keys. '
                'Use rzp_test_... keys for testing, rzp_live_... for production. '
                'Changes take effect immediately without redeploying.'
            ),
            'fields': ('razorpay_key_id', 'razorpay_key_secret'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'subtotal']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'guest_token_short', 'item_count', 'total', 'updated_at']
    readonly_fields = ['user', 'guest_token', 'created_at', 'updated_at']
    inlines = [CartItemInline]

    def guest_token_short(self, obj):
        return obj.guest_token[:8] if obj.guest_token else '—'
    guest_token_short.short_description = 'Guest Token'

    def item_count(self, obj):
        return obj.count
    item_count.short_description = 'Items'

    def has_add_permission(self, request):
        return False


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used']
    search_fields = ['email']
    readonly_fields = ['email', 'otp', 'created_at', 'expires_at', 'is_used']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
