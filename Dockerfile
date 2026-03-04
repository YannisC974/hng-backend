FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système pour psycopg2, Pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- SECTION PRO : SÉCURITÉ ---
# Création d'un utilisateur système "django" pour ne pas tourner en root
RUN addgroup --system django && adduser --system --group django

# Installation des dépendances
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copie du projet et changement de propriétaire pour l'utilisateur django
COPY --chown=django:django . .

# Collecte des fichiers statiques (nécessaire pour la prod)
RUN python manage.py collectstatic --noinput

# On passe sur l'utilisateur restreint
USER django

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]