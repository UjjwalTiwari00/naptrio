# NAPTRIO — Django storefront

Production-ready Django scaffold for the Naptrio Audio India website.
A pixel-faithful HTML version of the homepage lives at the project root
(`index.html`) — that's the visual reference. This directory ports it
into a real Django project with template inheritance, reusable
includes, and a clean URL map.

---

## Folder structure

```
django_project/
├── manage.py
├── requirements.txt
├── Dockerfile · Procfile · .env.example · .gitignore
├── tailwind.config.js · postcss.config.js
├── naptrio/                     # project package
│   ├── settings.py              # env-aware settings (DEBUG, ALLOWED_HOSTS via .env)
│   ├── urls.py                  # root URLconf
│   ├── wsgi.py / asgi.py
├── store/                       # storefront app
│   ├── apps.py
│   ├── urls.py                  # / · /category/<slug>/ · /product/<id>/ · /cart/ · /subscribe/
│   ├── views.py                 # thin views, render templates
│   └── products.py              # static catalog (swap for ORM later)
├── templates/
│   ├── base.html                # <html> shell + meta + Tailwind + fonts
│   ├── partials/
│   │   ├── header.html          # sticky black header + nav + search + promo
│   │   ├── promo.html           # "Diwali Deals…" banner
│   │   ├── footer.html          # 5-col footer + newsletter
│   │   └── product_card.html    # reusable card include
│   └── store/
│       ├── home.html · category.html · product_detail.html
│       ├── about.html · contact.html · corporate.html · cart.html
└── static/
    ├── css/styles.css           # brand tokens + animations
    ├── js/app.js                # slideshow, rails, cart, subscribe AJAX
    └── img/naptrio-logo.png
```

---

## Installation

```bash
cd django_project
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # then edit the secret key
python manage.py migrate
python manage.py createsuperuser     # optional, for /admin
```

## Run (development)

```bash
python manage.py runserver
# → http://127.0.0.1:8000/
```

The base template loads Tailwind from the CDN, so the site renders
immediately — no Node build needed for dev.

## Tailwind production build (optional)

For production, swap the CDN script in `base.html` for a compiled
stylesheet. From this directory:

```bash
npm init -y
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss \
  -c tailwind.config.js \
  -i static/css/tailwind.src.css \
  -o static/css/tailwind.build.css \
  --minify
```

Then in `templates/base.html` replace the
`<script src="https://cdn.tailwindcss.com"></script>` line with:

```html
<link rel="stylesheet" href="{% static 'css/tailwind.build.css' %}" />
```

## Collect static (production)

```bash
python manage.py collectstatic --noinput
```

WhiteNoise (already wired into `MIDDLEWARE`) serves the compressed
hashed files directly — no Nginx config needed for static assets.

---

## Deployment

### Railway

1. Push this folder to a Git repo.
2. New Project → *Deploy from GitHub*.
3. Set env vars: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=your-app.railway.app`.
4. Railway auto-detects the `Procfile` and runs gunicorn.

### Vercel

Use the `vercel-python` runtime with a small `vercel.json` pointing at
`naptrio.wsgi:application`. Static files are best served via WhiteNoise
(already included). Vercel works but Railway / Fly / Render are
better-suited to long-running Django processes.

### Docker

```bash
docker build -t naptrio .
docker run -p 8000:8000 --env-file .env naptrio
```

### Nginx (VPS)

```nginx
server {
  listen 80;
  server_name naptrio.in;

  location /static/ { alias /srv/naptrio/staticfiles/; }
  location /media/  { alias /srv/naptrio/media/; }

  location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

Run gunicorn under systemd:
```ini
[Service]
WorkingDirectory=/srv/naptrio
ExecStart=/srv/naptrio/.venv/bin/gunicorn naptrio.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

---

## Next steps

The catalog currently lives as a Python list in `store/products.py` so
the site renders out of the box. Real models live just under the
surface — promote `Product` / `Category` to proper Django models, run
`makemigrations`, and update `views.py` to query the ORM. The
templates need no changes.
