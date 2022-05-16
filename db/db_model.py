import sqlalchemy as sq
from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config

engine = sq.create_engine(config.db_adress)
Base = declarative_base()


# Создание модели базы данных
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    favorite_user = relationship("FavoriteUser", back_populates="user")
    blocked_user = relationship("BlackList", back_populates="user")


class FavoriteUser(Base):
    __tablename__ = 'users_favorite'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    city = Column(String(25))
    age_interval = Column(String(6))
    link = Column(String)
    link_photo_list = Column(String)
    id_user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship("User", back_populates="favorite_user")


class BlackList(Base):
    __tablename__ = 'users_blacklist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_id = Column(Integer, unique=True)
    city = Column(String(25))
    age_interval = Column(String(6))
    link = Column(String)
    link_photo_list = Column(String)
    id_user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship("User", back_populates="blocked_user")


# Класс для работы с базой данных
class DbWorker:
    def __init__(self, user_id):
        self.user_id = user_id
        Base.metadata.create_all(bind=engine)
        self.session = sessionmaker(bind=engine)()

    # Регистрируем пользователя в бд
    def register_user(self):
        try:
            user = User(vk_id=self.user_id)
            self.session.add(user)
            self.session.commit()
            return True
        except (IntegrityError, InvalidRequestError):
            return False

    # Добавляем пару в список избранных
    def add_pair_in_favorite(self, pair_id, city, age_interval, link, link_photo):
        current_user = self.session.query(User).filter_by(vk_id=self.user_id).first()
        pair = FavoriteUser(
            vk_id=pair_id,
            city=city,
            age_interval=age_interval,
            link=link,
            link_photo_list=link_photo,
            id_user=current_user.id
            )
        self.session.add(pair)
        self.session.commit()
        return True

    # Добавляем пару в черный список
    def add_pair_in_blacklist(self, pair_id, city, age_interval, link, link_photo):
        current_user = self.session.query(User).filter_by(vk_id=self.user_id).first()
        pair = BlackList(
            vk_id=pair_id,
            city=city,
            age_interval=age_interval,
            link=link,
            link_photo_list=link_photo,
            id_user=current_user.id
            )
        self.session.add(pair)
        self.session.commit()
        return True

    # Удалить пару из избранных
    def delete_from_favorite(self, pair_id):
        pair = self.session.query(FavoriteUser).filter_by(vk_id=pair_id).first()
        self.session.delete(pair)
        self.session.commit()

    # Удалить пару из черного списка
    def delete_from_blacklist(self, pair_id):
        pair = self.session.query(BlackList).filter_by(vk_id=pair_id).first()
        self.session.delete(pair)
        self.session.commit()

    # Выдать список избранных по одному с помощью генератора
    def show_favorites(self):
        current_users_id = self.session.query(User).filter_by(vk_id=self.user_id).first()
        all_users_favourites = self.session.query(FavoriteUser).filter_by(id_user=current_users_id.id).all()
        for i in all_users_favourites:
            yield i

    # Выдать черный список по одному с помощью генератора
    def show_blacklist(self):
        current_users_id = self.session.query(User).filter_by(vk_id=self.user_id).first()
        all_users_blacklist = self.session.query(BlackList).filter_by(id_user=current_users_id.id).all()
        for i in all_users_blacklist:
            yield i

    # Проверка есть ли пользователь в бд
    def check_if_registered(self):
        if self.session.query(User).filter_by(vk_id=self.user_id).first():
            return True
        return False

    # Проверка есть ли пользователь в списке избранных
    def check_if_in_favorites(self, pair_id):
        if self.session.query(FavoriteUser).filter_by(vk_id=pair_id).first():
            return True
        return False

    # Проверка есть ли пользователь в черном списке
    def check_if_in_blacklist(self, pair_id):
        if self.session.query(BlackList).filter_by(vk_id=pair_id).first():
            return True
        return False
