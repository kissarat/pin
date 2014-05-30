import web
from mypinnings.conf import settings
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine


db = None

def connect_db():
    global db
    if db is not None:
        return db
    db = web.database(**settings.params)
    return db

def dbget(table, row_id):
    global db
    rows = db.select(table, where='id = $id', vars={'id': row_id})
    return rows[0] if rows else None

def get_db():
    global db
    return db

def create_db_connection_string():
    params = {'user': settings.params.get('user'),
       'pwd': settings.params.get('pw'),
       'host': settings.params.get('host'),
       'dbn': settings.params.get('dbn'),
       'db': settings.params.get('db')}
    return "%(dbn)s://%(user)s:%(pwd)s@%(host)s/%(db)s" % params




def load_sqla(handler):
    """
    A hook which loads SQLAlchemy
    """
    engine = create_engine(create_db_connection_string(), echo=True)
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
       web.ctx.orm.commit()
       raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # If the above alone doesn't work, uncomment
        # the following line:
        #web.ctx.orm.expunge_all()
