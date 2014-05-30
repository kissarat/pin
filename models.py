from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String



from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Like(Base):
    __tablename__ = 'likes'

    user_id = Column(Integer, primary_key=True)
    pin_id = Column(Integer, primary_key=True)

    def __init__(self, pin_id, user_id):
        self.user_id = user_id
        self.pin_id = pin_id

    def __repr__(self):
       return "<Like('%s','%s', '%s')>" % (self.user_id, self.pin_id)


users_table = Like.__table__
metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
