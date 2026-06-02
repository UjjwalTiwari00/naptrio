import random
import string

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from store.cart import merge_guest_cart
from store.email_utils import send_otp_email
from store.models import Category, Customer, EmailOTP, Order


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

def _generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def signup(request):
    """Step 1 — collect details, send OTP, store pending data in session."""
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
            otp = _generate_otp()
            expires_at = timezone.now() + timezone.timedelta(minutes=10)

            # Invalidate any previous unused OTPs for this email
            EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)

            EmailOTP.objects.create(email=email, otp=otp, expires_at=expires_at)

            # Stash form data in session (never store plain password — store it
            # temporarily so we can create the user after OTP passes)
            request.session['pending_signup'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'password': password,
            }
            request.session.modified = True

            sent = send_otp_email(email, otp, first_name)
            if sent:
                messages.success(request, f'A 6-digit OTP has been sent to {email}. Please check your inbox.')
            else:
                messages.warning(request, 'Could not send OTP email (SMTP not configured). Contact support.')

            return redirect('core:verify_otp')

    return render(request, 'accounts/signup.html', _ctx(request))


def verify_otp(request):
    """Step 2 — validate OTP, create account, log in."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    pending = request.session.get('pending_signup')
    if not pending:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('core:signup')

    if request.method == 'POST':
        entered = ''.join(filter(str.isdigit, request.POST.get('otp', '')))
        email = pending['email']

        otp_obj = (
            EmailOTP.objects
            .filter(email=email, is_used=False)
            .order_by('-created_at')
            .first()
        )

        if not otp_obj:
            messages.error(request, 'No OTP found. Please sign up again.')
            return redirect('core:signup')

        if otp_obj.is_expired:
            messages.error(request, 'OTP has expired. Please sign up again.')
            otp_obj.is_used = True
            otp_obj.save(update_fields=['is_used'])
            request.session.pop('pending_signup', None)
            return redirect('core:signup')

        if otp_obj.otp != entered:
            messages.error(request, 'Incorrect OTP. Please try again.')
            return render(request, 'accounts/verify_otp.html', _ctx(request, email=email))

        # OTP correct — create user
        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])

        user = User.objects.create_user(
            username=pending['email'],
            email=pending['email'],
            password=pending['password'],
            first_name=pending['first_name'],
            last_name=pending['last_name'],
        )
        if pending.get('phone'):
            user.customer.phone = pending['phone']
            user.customer.save()

        guest_token = getattr(request, 'guest_token', None)
        request.session.pop('pending_signup', None)
        login(request, user)
        merge_guest_cart(user, guest_token)
        messages.success(request, f"Welcome to NAPTRIO, {pending['first_name']}!")
        return redirect('core:dashboard')

    email = pending.get('email', '')
    return render(request, 'accounts/verify_otp.html', _ctx(request, email=email))


def resend_otp(request):
    """POST-only — regenerate and resend OTP for the pending signup."""
    pending = request.session.get('pending_signup')
    if not pending:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('core:signup')

    email = pending['email']
    otp = _generate_otp()
    expires_at = timezone.now() + timezone.timedelta(minutes=10)

    EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)
    EmailOTP.objects.create(email=email, otp=otp, expires_at=expires_at)
    request.session.modified = True

    sent = send_otp_email(email, otp, pending.get('first_name', ''))
    if sent:
        messages.success(request, f'A new OTP has been sent to {email}.')
    else:
        messages.warning(request, 'Could not send OTP email. Please contact support.')

    return redirect('core:verify_otp')


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
            guest_token = getattr(request, 'guest_token', None)
            login(request, user)
            merge_guest_cart(user, guest_token)
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
