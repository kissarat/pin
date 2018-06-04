from abc import abstractmethod
import json
import web
from api.utils import api_response, e_response

from mypinnings.database import connect_db


class BaseAPI(object):
    """
    Base class for API handler
    """
    # __slots__ = [
    #     'data', 'status', 'error_code', 'csid_from_server',
    #     'csid_from_client', 'client_token', 'notifications'
    # ]

    def __init__(self):
        self.status = 200
        self.error_code = ''
        self.csid_from_client = ''
        self.csid_from_server = ''
        self.client_token = ''
        self.notifications = ''
        self.data = {}

    @property
    def db(self):
        return connect_db()

    def GET(self):
        """
        Wrong HTTP method for API handling
        """
        return self.method_not_allowed()

    def POST(self):
        """
        Handler for API call. Must be overriden
        """
        return self.method_not_allowed()

    def method_not_allowed(self):
        self.status = 405
        self.error_code = "Method Not Allowed"
        return self.respond()

    def authenticate_by_token(self, logintoken):
        """Authenticates user by given logintoken

        Returns:
        status - flag set to True in case if user was successfully logged in
        user_dict - dictionary with users  profile data (if login success)
        access_denied - if login failure
        """
        user = self.db.select(
            'users',
            {"logintoken": logintoken},
            where="logintoken=$logintoken"
        )
        if len(user) > 0:
            return True, user[0]
        else:
            return False, e_response("Wrong login token" if logintoken
                                     else "Not received login token")

    @staticmethod
    def access_denied(error_code="Default error: access_denied"):
        """
        Access denied errors
        """
        data = {}
        status = 405
        return api_response(data=data, status=status, error_code=error_code)

    def respond(self):
        web.header('Content-Type', 'application/json')
        return json.dumps({
            "status": self.status,
            "error_code": self.error_code,
            "t_id": "",
            "s_version_id": "1.0",
            "csid_from_client": self.csid_from_client,
            "csid_from_server": self.csid_from_server,
            "client_token": self.client_token,
            "notifications": self.notifications,
            "data": self.data
        })


class BaseQueryRange(BaseAPI):
    def __init__(self):
        BaseAPI.__init__(self)
        # self.select = None
        self.range = None
        self.where = []
        self.select_vars = {}

    @abstractmethod
    def query(self):
        if len(self.where) > 0:
            self.where = ' AND '.join(self.where)
            sql = self.select % self.where
        else:
            sql = self.select
        if self.range:
            sql += ' limit %s offset %s' % self.range
        return self.db.query(sql, vars=self.select_vars)

    def query_range(self):
        request_data = web.input(page=1, items_per_page=10)
        page = request_data.get("page")
        items_per_page = request_data.get("items_per_page")

        if not page:
            page = 1
        else:
            page = int(page)
            if page < 1:
                page = 1
        if not items_per_page:
            items_per_page = 10
            if items_per_page < 1:
                items_per_page = 1
        else:
            items_per_page = int(items_per_page)

        # self.data['pages_count'] = math.ceil(float(len(self.data['image_id_list'])) /
        #                                 float(items_per_page))
        # self.data['pages_count'] = int(self.data['pages_count'])
        self.data['page'] = page
        self.data['items_per_page'] = items_per_page
        self.range = (items_per_page, (page-1) * items_per_page)
        return self.query()
