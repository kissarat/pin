from sqlalchemy import Column, Integer, String, Text, Boolean, Date, \
    ForeignKey
from sqlalchemy.orm import relationship, backref

from basemodel import Base, engine, Serializer
# from user import User

class PictureLike(Base, Serializer):
    __tablename__ = 'picture_likes'
    __table_args__ = {'extend_existing':True}
    __public__ = ['id', 'picture_id', 'user_id']

    id = Column(Integer, primary_key=True)
    picture_id = Column(Integer, ForeignKey("pictures.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    def __init__(self, picture_id, user_id):
        self.picture_id = picture_id
        self.user_id = user_id

    def __repr__(self):
       return "<Like(%s, %s)>" % (self.picture_id, self.picture_id)


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
