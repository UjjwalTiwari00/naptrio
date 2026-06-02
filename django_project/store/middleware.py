import uuid


GUEST_TOKEN_COOKIE = 'guest_token'
GUEST_TOKEN_MAX_AGE = 60 * 60 * 24 * 365  # 1 year


class GuestTokenMiddleware:
    """
    Sets a long-lived guest_token cookie on every response for anonymous
    users. This token is used to identify the guest's DB cart row so the
    cart survives browser close and session expiry.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach token to request so views/cart can read it cheaply
        request.guest_token = request.COOKIES.get(GUEST_TOKEN_COOKIE) or str(uuid.uuid4())

        response = self.get_response(request)

        # Write cookie if it wasn't already there (avoids resetting max-age on every hit)
        if GUEST_TOKEN_COOKIE not in request.COOKIES:
            response.set_cookie(
                GUEST_TOKEN_COOKIE,
                request.guest_token,
                max_age=GUEST_TOKEN_MAX_AGE,
                httponly=True,
                samesite='Lax',
            )

        return response
