from datetime import date
import urllib
import os.path

import web

from mypinnings import template
from mypinnings import database
from mypinnings import session
from mypinnings.admin.auth import login_required
from mypinnings import pin_utils


class Search(object):
    def GET(self):
        db = database.get_db()
        categories = db.where(table='categories', order='position desc, name')
        return template.admin.pins_search(categories)


class SearchCriteria(object):
    @login_required
    def GET(self):
        data = web.input(pin_url=None,
                         username=None,
                         name=None,
                         email=None)
        sess = session.get_session()
        sess['search_pin_url'] = data.pin_url
        sess['search_username'] = data.username
        sess['search_name'] = data.name
        sess['search_email'] = data.email
        sess['category'] = data.category
        sess['search_reset_offset'] = True
        
        where_clause = build_where(self)
        db = database.get_db()
        count = db.query('select count(*) as cnt from pins where %s' % ' and '.join(where_clause))[0]
        return count.cnt


PAGE_SIZE = 50


class SearchPagination(object):
    @login_required
    def GET(self):
        data = web.input(page=1, dir='desc', sort='pins.timestamp')
        sess = session.get_session()
        reset_offset = sess.get('search_reset_offset', False)
        if reset_offset:
            self.page = 0
            sess['search_reset_offset'] = False
        else:
            self.page = int(data.page) - 1
        self.sort = data.sort
        self.sort_direction = data.dir
        
        where_clause = build_where(self)
        db = database.get_db()
        results = db.query('''select 
                            pins.*,
                            case when users.username is null then '---' else users.username end as username
                        from pins 
                            left join users on pins.user_id=users.id
                        where {where_clause}
                        order by {sort_ord} {sort_dir}
                        limit {limit} offset {offset}
                        '''.format(where_clause=' and '.join(where_clause), sort_ord=self.sort, sort_dir=self.sort_direction, limit=PAGE_SIZE, offset=(PAGE_SIZE * self.page)))
        pins = []
        for row in results:
            pins.append(row)
        if pins:
            return web.template.frender('t/admin/pin_search_list.html')(pins, date)
        else:
            return web.template.frender('t/admin/pin_search_list.html')([], date)


class Pin(object):
    @login_required
    def GET(self, pin_id):
        db = database.get_db()
        try:
            pin = db.where(table='pins', id=pin_id)[0]
        except IndexError:
            return "Pin does not exist"
        selected_categories = set([c.category_id for c in db.where(table='pins_categories', pin_id=pin_id)])
        tags = db.where(table='tags', pin_id=pin_id)
        categories = [c for c in db.where(table='categories', order='position desc, name')]
        size = len(categories) / 3
        categories1 = categories[:size]
        categories2 = categories[size:2*size]
        categories3 = categories[2*size:]
        return web.template.frender('t/admin/pin_edit_form.html')(pin, selected_categories, tags, categories1, categories2, categories3)

    @login_required
    def POST(self, pin_id):
        db = database.get_db()
        pin = db.where(table='pins', id=pin_id)[0]
        data = web.input(image_file={})
        pin_utils.update_base_pin_information(db,
                                              pin_id=pin_id,
                                              user_id=pin.user_id,
                                              title=data.title,
                                              description=data.description,
                                              link=data.link,
                                              tags=data.tags,
                                              price=data.price,
                                              product_url=data.product_url,
                                              price_range=data.price_range,
                                              board_id=pin.board_id)
        categories = [int(v) for k, v in data.items() if k.startswith('category')]
        pin_utils.update_pin_into_categories(db=db,
                                             pin_id=pin_id,
                                             category_id_list=categories)
        if data.image_url:
            filename, _ = urllib.urlretrieve(data.image_url)
            pin_utils.update_pin_images(db=db,
                                        pin_id=pin_id,
                                        user_id=pin.user_id,
                                        image_filename=filename)
        return web.seeother('{}'.format(pin_id))

    @login_required
    def DELETE(self, pin_id):
        db = database.get_db()
        pin = db.where(table='pins', id=pin_id)[0]
        pin_utils.delete_pin_from_db(db=db,
                                     pin_id=pin_id,
                                     user_id=pin.user_id)
        return 'ok'


class MultipleDelete(object):

    @login_required
    def POST(self):
        data = web.input(ids='')
        ids = [int(x) for x in data.ids.split(',')]
        db = database.get_db()
        for pin_id in ids:
            pin = db.where(table='pins', what='id, user_id', id=pin_id)[0]
            pin_utils.delete_pin_from_db(db, pin_id, pin.user_id)
        return 'ok'

def build_where(self):
    sess = session.get_session()
    self.pin_url = sess.get('search_pin_url', None)
    self.category = sess.get('category', False)
    self.username = sess.get('search_username', False)
    self.full_name = sess.get('search_name', False)
    self.email = sess.get('search_email', False)
    
    where_clause = ['True']
    # where_clause must have columns only from pins table referenced directly since count query uses just the pins table
    if self.pin_url:
        if '/' in self.pin_url:
            # is a path
            external_id = self.pin_url.split('/')[-1]
        else:
            external_id = self.pin_url
        where_clause.append("pins.external_id='%s'" % external_id)
    if self.category == 'uncategorized':
        where_clause.append('pins.id not in (select pin_id from pins_categories)')
    elif self.category and self.category != 'any':
        where_clause.append('pins.id in (select pin_id from pins_categories where category_id=%d)' % int(self.category))
    
    db = database.get_db()
    user_list = None
    if self.username:
        user_list = db.select(tables='users', where='username=$username',
                            vars={'username': self.username})
    elif self.full_name:
        user_list = db.select(tables='users',
                            where="name like '%%{query}%%'".format(query=self.full_name))
    elif self.email:
        user_list = db.select(tables='users', where='email=$email',
                            vars={'email': self.email})
    if user_list:
        user_id_list = [str(row.id) for row in user_list]
        if user_id_list:
            where_clause.append('user_id in (%s)' % ','.join(user_id_list))
    elif self.username or self.full_name or self.email:
        if self.username == '---':
            where_clause.append('user_id not in (select id from users)')
        else:
            where_clause.append('False')
    
    return where_clause
