import web
from web import form

import mypinnings.session
from mypinnings.template import tpl, ltpl, lmsg
from mypinnings.auth import force_login
from mypinnings.conf import settings
from mypinnings.database import connect_db, dbget
db = connect_db()

urls = ('', 'PageEditProfile',
        '/(email)', 'PageEditProfile',
        '/(profile)', 'PageEditProfile',
        '/(password)', 'PageEditProfile',
        '/(social-media)', 'PageEditProfile',
        '/(privacy)', 'PageEditProfile',
        '/(email-settings)', 'PageEditProfile',
        '/changeemail', 'PageChangeEmail',
        '/changepw', 'PageChangePw',
        '/changesm', 'PageChangeSM',
        '/changeprivacy', 'PageChangePrivacy',
        )

app = web.application(urls, locals())
mypinnings.session.initialize(app)
sess = mypinnings.session.sess

class PageEditProfile:
    _form = form.Form(
        form.Textbox('name'),
        form.Dropdown('country', []),
        form.Textbox('hometown'),
        form.Textbox('city'),
        form.Textbox('zip'),
        form.Textbox('username'),
        form.Textbox('website'),
        form.Textarea('about'),
    )

    def GET(self, name=None):
        force_login(sess)
        user = dbget('users', sess.user_id)
        photos = db.select('photos', where='album_id = $id', vars={'id': sess.user_id})
        msg = web.input(msg=None)['msg']
        return ltpl('editprofile', user, settings.COUNTRIES, name, photos, msg)

    def POST(self, name=None):
        user = dbget('users', sess.user_id)
        force_login(sess)

        form = self._form()
        if not form.validates():
            return 'you need to fill in everything'

        db.update('users', where='id = $id',
            name=form.d.name, about=form.d.about, username=form.d.username,
            zip=(form.d.zip or None), website=form.d.website, country=form.d.country,
            hometown=form.d.hometown, city=form.d.city,
            vars={'id': sess.user_id})
        get_input = web.input(_method='get')
        if 'user_profile' in get_input:
            raise web.seeother('/%s?editprofile=1' % user.username)
        raise web.seeother('/settings/profile')

class PageChangeEmail:
    _form = form.Form(
        form.Textbox('email'),
        form.Textbox('username'))

    # @csrf_protected # Verify this is not CSRF, or fail
    def POST(self):
        force_login(sess)

        form = self._form()
        if not form.validates():
            return 'you need to fill in everything'
        if db.select('users', where='email = $email', vars={'email' : form.d.email}):
            return 'Pick another email address'
        if db.select('users', where='username = $username', vars={'username':form.d.username}):
            return 'Pick another username'
        db.update('users', where='id = $id', vars={'id': sess.user_id}, email=form.d.email, username=form.d.username)
        raise web.seeother('/settings/email')

class PageChangePw:
    _form = form.Form(
        form.Textbox('old'),
        form.Textbox('pwd1'),
        form.Textbox('pwd2')
    )

    def POST(self):
        force_login(sess)

        form = self._form()
        if not form.validates():
            raise web.seeother('/settings/password?msg=bad input', absolute=True)

        # user = dbget('users', sess.user_id)
        # if not user:
        #     raise web.seeother('/settings/password?msg=error getting user', absolute=True)

        # if form.d.pwd1 != form.d.pwd2:
        #     raise web.seeother('/settings/password?msg=Your passwords don\'t match!', absolute=True)

        if not form.d.pwd1 or len(form.d.pwd1) < 6:
            raise web.seeother('/settings/password?msg=Your password must have at least 6 characters.', absolute=True)

        # if not auth.authenticate_user_username(user.username, form.d.old):
        #     raise web.seeother('/settings/password?msg=Your old password did not match!', absolute=True)

        logintoken = convert_to_logintoken(sess.user_id)

        if logintoken:
            data = {
                "old_password": form.d.old,
                "new_password": form.d.pwd1,
                "new_password2": form.d.pwd2,
                "logintoken": logintoken
            }

            data = api_request("api/profile/pwd", "POST", data)
            if data['status'] == 200:
                raise web.seeother('/settings/password')
            else:
                msg = data['error_code']
                raise web.seeother('/settings/password?msg=%s' % msg, absolute=True)


        # auth.chage_user_password(sess.user_id, form.d.pwd1)

class PageChangeSM:
    _form = form.Form(
        form.Textbox('facebook'),
        form.Textbox('linkedin'),
        form.Textbox('twitter'),
        form.Textbox('gplus'),
    )

    def POST(self):
        force_login(sess)

        form = self._form()
        if not form.validates():
            return 'bad input'

        user = dbget('users', sess.user_id)
        if not user:
            return 'error getting user'

        db.update('users', where='id = $id', vars={'id': sess.user_id}, **form.d)
        raise web.seeother('/settings/social-media')

class PageChangePrivacy:
    _form = form.Form(
        form.Checkbox('private'),
    )

    def POST(self):
        force_login(sess)

        form = self._form()
        form.validates()

        db.update('users', where='id = $id', vars={'id': sess.user_id}, **form.d)
        raise web.seeother('/settings/privacy')