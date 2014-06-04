from sqlalchemy import Column, Integer, String, Text, Boolean, Date, \
    ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import text

from basemodel import Base, engine, Serializer
# from user import User

class PictureComment(Base, Serializer):
    __tablename__ = 'picture_comments'
    __table_args__ = {'extend_existing':True}
    __public__ = ['id', 'picture_id', 'user_id', 'user']

    id = Column(Integer, primary_key=True)
    picture_id = Column(Integer, ForeignKey("pictures.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    comment = Column(Text, default='')
    timestamp = Column(Integer,
                       server_default=text("date_part('epoch', now())"))

    def __init__(self, picture_id, user_id, comment):
        self.picture_id = picture_id
        self.user_id = user_id
        self.comment = comment

    def __repr__(self):
       return "<Comment(%s, %s)>" % (self.picture_id, self.picture_id, self.comment)


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
