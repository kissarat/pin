import web

from api.views.base import BaseAPI
from api.utils import api_response
from mypinnings.database import connect_db

db = connect_db()


class GetCategories(BaseAPI):
    """
    API for receiving list of categories
    """
    def POST(self):
        return api_response({
            'categories_list': list(
                db.select(
                    'categories',
                    order='position desc, name',
                    where='parent is null'
                )
            )
        })