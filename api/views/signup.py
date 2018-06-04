import web
import random
from sqlalchemy import update
from api.models.user import User

from api.utils import api_response, save_api_request, e_response, authenticate
from api.views.base import BaseAPI

from mypinnings.database import connect_db
from mypinnings.auth import login_user
from mypinnings.register import add_default_lists, send_activation_email
from mypinnings import auth
from mypinnings import session
from ser import sess


db = connect_db()


class Auth(BaseAPI):
    def POST(self):
        """
            Authentification method for API
        """
        request_data = web.input()
        save_api_request(request_data)
        email = request_data.get("email")
        if not email:
            return e_response('username or email is required', 400)
        password = request_data.get("password")
        if not password:
            return e_response('password is required', 400)
        user = self.authenticate(email, password)
        if not user:
            return self.access_denied("Login or password wrong")
        login_user(sess, user.get('id'))
        self.data["user_id"] = user.get("id")
        self.data["email"] = user.get("email")
        self.data["username"] = user.get("username")
        return self.respond()

    @staticmethod
    def authenticate(username, password):
        user = web.ctx.orm.query(User)\
            .filter(User.username == username or User.email == username)\
            .first()
        if not user:
            return
        pw_hash = str(hash(password))
        pw_salt = user['pw_salt']
        pw_hash = str(hash(pw_hash + pw_salt))
        if pw_hash == user['pw_hash']:
            return user


class Register(BaseAPI):
    """
        Register method for API
    """
    def POST(self):
        """
            Method register must receive next additional params:

            uname - user name
            pwd - user password
            email - user email
            complete_name - user first name
            language - user language

            output response also included:

            login_token for new user,
            hashed_activation for activation-email
        """
        request_data = web.input()
        data = {}

        save_api_request(request_data)
        csid_from_client = request_data.get('csid_from_client')

        uname = request_data.get("uname")
        pwd = request_data.get("pwd")
        email = request_data.get("email")
        complete_name = request_data.get("complete_name")
        # last_name = request_data.get("last_name")
        language = str(request_data.get("language", "en"))

        status_error = 200
        error_code = ""

        status, error_code = self.register_validation(uname, pwd,
                                                      email, complete_name)
        if status:
            activation = random.randint(1, 10000)
            hashed = hash(str(activation))

            user_id = auth.create_user(email, pwd,
                                       name=complete_name,
                                       username=uname,
                                       activation=activation,
                                       locale=language)

            add_default_lists(user_id)
            send_activation_email(email, hashed, user_id)
            sess = session.get_session()
            auth.login_user(sess, user_id)
            user = db.select('users', {'id': user_id}, where='id=$id')[0]
            login_token = user.get('logintoken')
            data.update({
                "logintoken": login_token,
                # "hashed_activation": hashed,
                })
        else:
            status_error = 405

        response = api_response(
            data,
            status=status_error,
            error_code=error_code,
            csid_from_client=csid_from_client,)

        return response

    def register_validation(self, uname, pwd, email, complete_name):
        """
            Validation entered user's request parameters:
            name, password,
            email, complete_name
        """
        request_params = {
            "uname": uname,
            "pwd": pwd,
            "email": email,
            "complete_name": complete_name,
        }
        error_code = ""
        for field, value in request_params.items():
            if value is None:
                error_code = "Not entered necessary parameter '"
                error_code += str(field)+"' for register method SignUp APIs"
                return False, error_code

        pwd_status, error_code = auth.check_password(uname, pwd, email)
        if not pwd_status:
            return False, error_code

        if auth.email_exists(email):
            error_code = 'Sorry, that email already exists.'
            return False, error_code

        if auth.username_exists(uname):
            error_code = 'Sorry, that username already exists.'
            return False, error_code

        return True, error_code


class ConfirmUser(BaseAPI):
    """Confirmation of user email

    Response:
        status = 200 or error_code
    """
    @authenticate
    def POST(self):
        """
        Compare given activation code with existed.
        If they are identical - activate new user
        """
        hashed_activation = web.input().get("hashed_activation")
        activation = self.user.get('activation')
        if not hashed_activation:
            return e_response("Not found hashed_activation field in request", 400)
        if hash(str(activation)) != int(hashed_activation):
            return e_response("Wrong activation code given from user", 403)

        update(User).where(User.id == self.user['id']).values(activation=0)
        # db.update('users', activation=0,
        #           vars={'id': self.user["id"]}, where="id=$id")

        return self.respond()


class ResendActivation(BaseAPI):
    """
    Method that resends activation letter
    """
    def POST(self):
        request_data = web.input()

        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        csid_from_client = request_data.get('csid_from_client')
        logintoken = request_data.get('logintoken')
        user_status, user = self.authenticate_by_token(logintoken)

        # User id contains error code
        if not user_status:
            return user

        activation = user['activation']

        if activation == 0:
            status = 400
            error_code = "Your account is already activated"
        else:
            user_id = user['id']
            email = user['email']

            hashed = hash(str(activation))

            send_activation_email(email, hashed, user_id)

        response = api_response(data=data,
                                status=status,
                                error_code=error_code,
                                csid_from_client=csid_from_client,
                                csid_from_server=csid_from_server)

        return response
