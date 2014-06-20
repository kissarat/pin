from sqlalchemy import *
import basemodel


class Query(basemodel.Base, basemodel.Serializer):
    __tablename__ = 'queries'
    __table_args__ = {'extend_existing': True}
    __public__ = ['string', 'timestamp']

    string = Column(String)
    timestamp = Column(Integer,
                       primary_key=True,
                       server_default=text("date_part('epoch'::text, now())"))

    def __init__(self, string):
        self.string = string
