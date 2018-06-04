import web

from api.models.user import User
from api.views.base import BaseAPI
from api.utils import api_response, save_api_request, e_response, authenticate

from mypinnings.database import connect_db, dbget


class Notification(BaseAPI):
    @authenticate
    def POST(self):
        """
        Return list of user notifications sorted by timestamp
        depeds on user logintoken
        """
        self.data = self.notifications
        self.notifications = {}
        return self.respond()


class CreateNotification(BaseAPI):
    """
    Responsible for notifications creation
    """
    def POST(self):
        """
        Example usage:
        curl --data "csid_from_client=11&user_id=78&msg=message&url=some_url" \
        http://localhost:8080/api/notification/add
        """
        params = web.input()
        required = {'user_id', 'msg', 'url'}
        required -= set(params.keys())
        if len(required) > 0:
            return e_response(', '.join(required) + ' is required', 400)
        if not params["user_id"].isdigit():
            return e_response('user_id must be positive integer', 400)
        user_id = int(params["user_id"])
        if 0 == web.ctx.orm.query(User).filter(User.id == user_id).count():
            return e_response('User with id %s is not found' % user_id, 404)
        try:
            self.db.insert('notifs', user_id=user_id, message=params["msg"], link=params["url"])
        except Exception as ex:
            return e_response(ex.message)
        return self.respond()


class GetNotification(BaseAPI):
    """
    Allows to get individual notifications
    """
    @authenticate
    def POST(self, notification_id):
        """ Method responsible for retuning individual notifications

        :args: logintoken, csid_from_client, notification_id.
        :returns: notification_or_404
        :to_test: curl --data "csid_from_client=1&logintoken=zs4jxj0yM2"\
        http://localhost:8080/api/notification/177
        """
        self.data = dbget('notifs', notification_id)

        # Do not allow to read notification related to other users
        if self.data.user_id != self._user.id:
            return e_response('User can access to his own notifications only', 403)

        # Remove notification which was already reviewed
        self.db.delete('notifs', where='id = $id', vars={'id': notification_id})
        return self.respond()
