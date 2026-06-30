from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.core.config import settings

sync_engine = create_engine(settings.sync_database_url, echo=False)
SyncSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)
