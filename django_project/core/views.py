from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from store.models import Category, Customer, Order


# ── helpers ───────────────────────────────────────────────────────────────────

def _ctx(request, **extra):
    ctx = {
        'nav_categories': list(Category.objects.all()),
        'promo_text': 'Diwali Deals from Nov 5 – Nov 10 2026',
        'active_slug': None,
    }
    ctx.update(extra)
    return ctx


# ── auth ──────────────────────────────────────────────────────────────────────

def signup(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        phone      = request.POST.get('phone', '').strip()
        password   = request.POST.get('password', '')
        confirm    = request.POST.get('confirm_password', '')

        if not all([first_name, email, password]):
            messages.error(request, 'First name, email and password are required.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            if phone:
                user.customer.phone = phone
                user.customer.save()
            login(request, user)
            messages.success(request, f'Welcome to NAPTRIO, {first_name}!')
            return redirect('core:dashboard')

    return render(request, 'accounts/signup.html', _ctx(request))


def signin(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user:
            login(request, user)
            next_url = request.GET.get('next') or 'core:dashboard'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/signin.html', _ctx(request))


def signout(request):
    logout(request)
    return redirect('store:home')


# ── account pages ─────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    customer      = request.user.customer
    recent_orders = Order.objects.filter(customer=customer).prefetch_related('items__product')[:3]
    ctx = _ctx(request, customer=customer, recent_orders=recent_orders)
    return render(request, 'accounts/dashboard.html', ctx)


@login_required
def orders(request):
    customer   = request.user.customer
    all_orders = Order.objects.filter(customer=customer).prefetch_related('items__product')
    ctx = _ctx(request, customer=customer, orders=all_orders)
    return render(request, 'accounts/orders.html', ctx)


@login_required
def order_detail(request, order_id):
    customer = request.user.customer
    order    = get_object_or_404(Order, id=order_id, customer=customer)
    ctx = _ctx(request, customer=customer, order=order)
    return render(request, 'accounts/order_detail.html', ctx)


@login_required
def edit_profile(request):
    user     = request.user
    customer = user.customer

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        user.save()

        customer.phone   = request.POST.get('phone', '').strip()
        customer.address = request.POST.get('address', '').strip()
        customer.city    = request.POST.get('city', '').strip()
        customer.state   = request.POST.get('state', '').strip()
        customer.pincode = request.POST.get('pincode', '').strip()
        customer.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('core:dashboard')

    ctx = _ctx(request, customer=customer)
    return render(request, 'accounts/edit_profile.html', ctx)
