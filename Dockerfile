# Utilisation d'une image légère de Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .

# Installer les dépendances nécessaires
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port 5110 pour Flask
EXPOSE 5110

# Commande pour exécuter l'application
CMD ["python", "app.py"]
