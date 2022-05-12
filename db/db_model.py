import sqlalchemy as sq
from sqlalchemy import create_engine, Table, Integer, String, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


engine = sq.create_engine('postgresql://postgres:575863@localhost:5432/VKinder')
Base = declarative_base()



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


class DbWorker:
    def __init__(self, user_id):
        self.user_id = user_id
        Base.metadata.create_all(bind=engine)
        self.session = sessionmaker(bind=engine)()

    def register_user(self):
        try:
            user = User(vk_id=self.user_id)
            self.session.add(user)
            self.session.commit()
            print('Юзер зареган')
            return True
        except (IntegrityError, InvalidRequestError):
            print('Юзер не зареган')
            return False

    def add_pair_in_favorite(self, pair_id, city, age_interval, link, link_photo):
        current_user = self.session.query(User).filter_by(vk_id=self.user_id).first()
        try:
            # Мб добавить в переменную id user'a
            pair = FavoriteUser(
                vk_id=pair_id,
                city=city,
                age_interval=age_interval,
                link=link,
                link_photo_list=link_photo,
                id_user=current_user.id
            )
            self.session.add(pair)
            # Мб превратить в переменную и в скобки убрать
            self.session.commit()
            print('юзер добавлен в избранное')
            return True
        except (IntegrityError, InvalidRequestError):
            print('юзер не добавлен в избранное')
            return False

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
        print('юзер добавлен в блеклист')
        return True
        # except (IntegrityError, InvalidRequestError):
        #     print('юзер не добавлен в блеклист')
        #     return False

    def delete_from_favorite(self, pair_id):
        pair = self.session.query(FavoriteUser).filter_by(vk_id=pair_id).first()
        self.session.delete(pair)
        self.session.commit()

    def delete_from_blacklist(self, pair_id):
        pair = self.session.query(BlackList).filter_by(vk_id=pair_id).first()
        self.session.delete(pair)
        self.session.commit()

    def show_favorites(self):
        current_users_id = self.session.query(User).filter_by(vk_id=self.user_id).first()
        all_users_favourites = self.session.query(FavoriteUser).filter_by(id_user=current_users_id.id).all()
        for i in all_users_favourites:
            yield i

    def show_blacklist(self):
        current_users_id = self.session.query(User).filter_by(vk_id=self.user_id).first()
        all_users_blacklist = self.session.query(BlackList).filter_by(id_user=current_users_id.id).all()
        for i in all_users_blacklist:
            yield i

    def check_if_registered(self):
        if self.session.query(User).filter_by(vk_id=self.user_id).first():
            return True
        return False

    def check_if_in_favorites(self, pair_id):
        if self.session.query(FavoriteUser).filter_by(vk_id=pair_id).first():
            return True
        return False

    def check_if_in_blacklist(self, pair_id):
        if self.session.query(BlackList).filter_by(vk_id=pair_id).first():
            return True
        return False


