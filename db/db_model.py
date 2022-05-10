import sqlalchemy as sq
from sqlalchemy import create_engine, Table, Integer, String, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base


from sqlalchemy.orm import sessionmaker

engine = sq.create_engine('postgresql://postgres:575863@localhost:5432/Vkinder')
connection = engine.connect()
Base = declarative_base()
Session = sessionmaker()
session = Session


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)


class FavoriteUser(Base):
    __tablename__ = 'users_favorite'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    city = Column(String(25))
    age_interval = Column(String(6))
    link = Column(String)
    link_photo_list = Column(String)
    id_user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))


class BlackList(Base):
    __tablename__ = 'users_blacklist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    city = Column(String(25))
    age_interval = Column(String(6))
    link = Column(String)
    link_photo_list = Column(String)
    id_user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))


# Base.metadata.create_all(engine)

class DbWorker:
    def __init__(self, user_id):
        self.user_id = user_id



    def register_user(self):
        try:
            session.add(User(vk_id=self.user_id))
            session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False

    def add_pair_in_favorite(self, pair_id, city, age_interval, link, link_photo):
        try:
            # Мб добавить в переменную id user'a
            session.add(FavoriteUser(
                vk_id=pair_id,
                city=city,
                age_interval=age_interval,
                link=link,
                link_photo_list=link_photo,
                id_user=self.user_id
            ))
            # Мб превратить в переменную и в скобки убрать
            session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False

    def add_pair_in_blacklist(self, pair_id, city, age_interval, link, link_photo):
        try:
            session.add(BlackList(
                vk_id=pair_id,
                city=city,
                age_interval=age_interval,
                link=link,
                link_photo_list=link_photo,
                id_user=self.user_id
            ))
            session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False

    def delete_from_favorite(self, pair_id):
        pair = session.query(FavoriteUser).filter_by(vk_id=pair_id).first()
        session.delete(pair)
        session.commit()

    def delete_from_blacklist(self, pair_id):
        pair = session.query(BlackList).filter_by(vk_id=pair_id).first()
        session.delete(pair)
        session.commit()

    def show_favorites(self):
        current_users_id = session.query(User).filter_by(vk_id=self.user_id).first()
        all_users_favourites = session.query(FavoriteUser).filter_by(id_user=current_users_id.id).all()
        yield all_users_favourites

    def show_blacklist(self):
        current_users_id = session.query(User).filter_by(vk_id=self.user_id).first()
        all_users_blacklist = session.query(BlackList).filter_by(id_user=current_users_id.id).all()
        yield all_users_blacklist

