# Permet d'indiquer que la fonction retourne un générateur (yield)
from collections.abc import Generator

# SQLAlchemy pour créer la connexion DB et exécuter des requêtes
from sqlalchemy import create_engine, delete
# Gestion des sessions ORM
from sqlalchemy.orm import Session, sessionmaker

# Récupération de la configuration (URL DB, etc.)
from app.core.config import get_settings
# Base ORM (toutes les tables héritent de Base)
from app.db.base import Base
# Modèle pour les tokens révoqués
from app.db.models import RevokedToken
# Service d’authentification (pour gérer les users et le temps UTC)
from app.services.auth import auth_service

# Chargement des paramètres de configuration
settings = get_settings()

# Dictionnaire pour config spécifique du moteur
engine_kwargs = {}

# Si on utilise SQLite → config spéciale (sinon erreur multi-thread)
if settings.database_url.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}

# Création du moteur de base de données
engine = create_engine(settings.database_url, **engine_kwargs)

# Création du "factory" de sessions DB
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,        # évite flush automatique
    autocommit=False,       # commit manuel obligatoire
    expire_on_commit=False  # garde les objets utilisables après commit
)


# Dépendance FastAPI pour récupérer une session DB
def get_db() -> Generator[Session, None, None]:
    # Création d'une session
    db = SessionLocal()
    try:
        # Fournit la session à la route (yield)
        yield db
    finally:
        # Ferme toujours la session (évite memory leak)
        db.close()


# Fonction d'initialisation de la base de données
def init_db() -> None:
    # Crée toutes les tables définies dans les modèles
    Base.metadata.create_all(bind=engine)

    # Ouvre une session DB
    with SessionLocal() as db:
        # Supprime les tokens expirés de la table revoked_tokens
        db.execute(
            delete(RevokedToken).where(
                RevokedToken.expires_at <= auth_service.utcnow()
            )
        )

        # Crée des utilisateurs par défaut (ex: admin)
        auth_service.seed_default_users(db)

        # Sauvegarde les changements
        db.commit()