from src.db.models import BulletinModel


class SyncBulletinRepository:
    def __init__(self, session):
        self.session = session

    def add_many(self, bulletins: list[BulletinModel]) -> None:
        self.session.add_all(bulletins)
        self.session.flush()

    def get_all(self) -> list[BulletinModel]:
        self.session.get(BulletinModel)
        return self.session.all()
