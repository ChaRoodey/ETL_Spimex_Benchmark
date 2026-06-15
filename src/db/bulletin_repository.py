from src.db.models import BulletinModel


class BulletinRepository:
    def __init__(self, session):
        self.session = session

    async def add_many(self, bulletins: list[BulletinModel]) -> None:
        self.session.add_all(bulletins)
        await self.session.flush()

    async def get_all(self) -> list[BulletinModel]:
        await self.session.get(BulletinModel)
        return await self.session.all()
