from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir))

from mypinnings.database import create_db_connection_string

engine = create_engine(create_db_connection_string(), echo=True)

Base = declarative_base()


class Serializer(object):
    __public__ = None

    def to_serializable_dict(self):
        dict_to_return = {}
        for public_key in self.__public__:
            value = getattr(self, public_key)
            if isinstance(value, list):
                dict_to_return[public_key] = \
                    [v.to_serializable_dict() for v in value]
            elif isinstance(value, Base):
                dict_to_return[public_key] = value.to_serializable_dict()
            else:
                if value is not None:
                    dict_to_return[public_key] = value
        return dict_to_return