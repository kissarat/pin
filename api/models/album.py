from sqlalchemy import Column, Integer, String, Text, Boolean, Date, \
    ForeignKey
from sqlalchemy.orm import relationship, backref

from basemodel import Base, engine, Serializer
from picture import Picture
# from user import User

class Album(Base, Serializer):
    __tablename__ = 'albums'
    __table_args__ = {'extend_existing':True}
    __public__ = ['id', 'user_id', 'slug', 'title', 'description', 'pictures', 'cover']

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    slug = Column(String(40), nullable=False)
    title = Column(String(250), default='')
    description = Column(Text, default='')
    pictures = relationship("Picture", primaryjoin=(id==Picture.album_id), post_update=True)

    cover_id = Column(Integer, ForeignKey('pictures.id',
                                        use_alter=True,
                                        name="fk_pic"))
    cover = relationship("Picture", primaryjoin=(cover_id==Picture.id),
                       backref=backref("cover", uselist=False), post_update=True)

    def __init__(self, user_id, slug, title='', description=''):
        self.user_id = user_id
        self.slug = slug
        self.title = title
        self.description = description

    def __repr__(self):
       return "<Album('%s', '%s', '%s')>" % (self.title, self.user_id, self.slug)


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
