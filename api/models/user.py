from sqlalchemy import Column, Integer, String, Text, Boolean, Date, \
    ForeignKey

from basemodel import Base, engine, Serializer
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import text

from album import Album
from picture import Picture

class User(Base, Serializer):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing':True}
    __public__ = ['id', 'email', 'name', 'username', 'timestamp',
        'pic', 'bg', 'hometown', 'city', 'website', 'pic_obj']

    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    pw_hash = Column(String)
    pw_salt = Column(String)
    about = Column(String)
    timestamp = Column(Integer,
                       server_default=text("date_part('epoch'::text, now())"))
    views = Column(Integer, default=0)
    show_views = Column(Boolean, default=True)
    username = Column(String)
    seriesid = Column(Text, default='')
    logintoken = Column(Text, default='')
    zip = Column(Integer)
    country = Column(Text, default='')
    website = Column(Text, default='')
    facebook = Column(Text, default='')
    linkedin = Column(Text, default='')
    twitter = Column(Text, default='')
    gplus = Column(Text, default='')

    # pic = Column(Integer)
    pic_id = Column(Integer, ForeignKey('pictures.id',
                                        use_alter=True,
                                        name="fk_pic"))
    pic_obj = relationship("Picture", primaryjoin=(pic_id==Picture.id),
                       backref=backref("user_pic", uselist=False))

    hometown = Column(String)
    city = Column(String)
    private = Column(Boolean, default=False)
    # bg = Column(Boolean, default=False)
    bg_id = Column(Integer, ForeignKey('pictures.id',
                                        use_alter=True,
                                        name="fk_bg"))
    bg = relationship("Picture", primaryjoin=(bg_id==Picture.id),
                      backref=backref("user_bg", uselist=False))

    bgx = Column(Integer, default=0)
    bgy = Column(Integer, default=0)
    activation = Column(Integer, default=0)
    # tsv tsvector,
    login_source = Column(String(length=2), nullable=False, default='MP')
    birthday = Column(Date)
    headerbgx = Column(Integer, default=0, nullable=False)
    headerbgy = Column(Integer, default=0, nullable=False)
    locale = Column(String(length=2), nullable=False, default='en')
    getlist_privacy_level = Column(Integer, default=1)
    is_pin_loader = Column(Boolean, default=False, nullable=False)
    albums = relationship("Album")

    def __init__(self, name, username, email, pw_hash, pw_salt):
        self.name = name
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
        self.pw_salt = pw_salt

    def __repr__(self):
       return "<User('%s', '%s', '%s')>" % (self.id, self.name, self.username)

    def to_serializable_dict(self):
        if self.pic_obj:
            self.pic = self.pic_obj.resized_url
        else:
            self.pic = None

        serializable_dict =  super(self.__class__, self).to_serializable_dict()

        return serializable_dict


metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
