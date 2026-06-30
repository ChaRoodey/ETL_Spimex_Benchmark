from src.db.models import BulletinModel


class AsyncBulletinRepository:
    def __init__(self, session):
        self.session = session

    async def add_many(self, bulletins: list[BulletinModel]) -> None:
        try:
            self.session.add_all(bulletins)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def get_all(self) -> list[BulletinModel]:
        await self.session.get(BulletinModel)
        return await self.session.all()
