""" Implements images part of the API """
import os
import web
import uuid
import datetime
import math
import random
import string

from mypinnings import database
from api.views.base import BaseAPI
from api.utils import api_response, save_api_request, e_response
from mypinnings.database import connect_db
from mypinnings.conf import settings
from mypinnings.media import store_image_from_filename

db = connect_db()

DIGITS_AND_LETTERS = string.ascii_letters + string.digits


class ImageUpload(BaseAPI):
    """ Handles image upload and storing it on the file system """
    def POST(self):
        """ Images upload main handler

        Can be tested using the following command:
        curl -F "image_title=some_title" -F "image_descr=some_descr" \
        -F "image_file=@/home/oleg/Desktop/hard.jpg" \
        http://localhost:8080/api/image/upload
        """
        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        request_data = web.input(image_file={})
        logintoken = request_data.get('logintoken')

        user_status, user = self.authenticate_by_token(logintoken)
        # User id contains error code
        if not user_status:
            return user

        csid_from_server = user['seriesid']
        csid_from_client = request_data.get("csid_from_client")

        save_api_request(request_data)
        file_obj = request_data.get('image_file')

        # For some reason, FileStorage object treats itself as False
        if type(file_obj) == dict:
            return api_response(data={}, status=405,
                                error_code="Required args are missing")

        file_path = self.save_file(file_obj)
        images_dict = store_image_from_filename(db,
                                                file_path,
                                                widths=(202, 212))

        external_id = _generate_external_id()

        image_kwargs = {'name': request_data.get("image_title"),
                        'description': request_data.get("image_descr"),
                        'user_id': user['id'],
                        'link': request_data.get("link"),
                        'product_url': request_data.get("product_url"),
                        'price': request_data.get("price"),
                        'price_range': request_data.get("price_range"),
                        'board_id': request_data.get("board_id"),
                        'external_id': external_id,
                        'image_url': images_dict[0]['url'],
                        'image_width': images_dict[0]['width'],
                        'image_height': images_dict[0]['height'],
                        'image_202_url': images_dict[202]['url'],
                        'image_202_height': images_dict[202]['height'],
                        'image_212_url': images_dict[212]['url'],
                        'image_212_height': images_dict[212]['height']}

        pin_id = self.create_db_record(image_kwargs)

        data['image_id'] = pin_id
        data['external_id'] = external_id

        response = api_response(data=data,
                                status=status,
                                error_code=error_code,
                                csid_from_client=csid_from_client,
                                csid_from_server=csid_from_server)

        return response

    def create_db_record(self, kwargs):
        """
        Creates image record in the database.
        """
        # Do not record empty fields
        kwargs = {key: value for (key, value) in kwargs.items()
                  if value is not None}
        return db.insert("pins", **kwargs)

    def save_file(self, file_obj, upload_dir=None):
        """
        Saves uploaded file to a given upload dir.
        """
        if not upload_dir:
            upload_dir = self.get_media_path()
        filename = file_obj.filename
        filename = self.get_file_name(filename, upload_dir)
        filepath = os.path.join(upload_dir, filename)
        upload_file = open(filepath, 'w')
        upload_file.write(file_obj.file.read())
        upload_file.close()
        return filepath

    def get_media_path(self):
        """
        Returns or creates media directory.
        """
        media_path = settings.MEDIA_PATH
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        return media_path

    def get_file_name(self, filename, upload_dir):
        """
        Method responsible for avoiding duplicated filenames.
        """
        filepath = os.path.join(upload_dir, filename)
        exists = os.path.isfile(filepath)
        # Suggest uuid hex as a filename to avoid duplicates
        if exists:
            filename = "%s.%s" % (uuid.uuid4().hex[:10], filename)
        return filename


class QueryBoardInfo(BaseAPI):
    """
    Class responsible for getting all pins from a given board

    :link: /api/image/query-board
    """
    def POST(self):
        """ Returns pin id's of a given board

        :param str csid_from_client: Csid string from client
        :param str board_name: name of a queried board
        :param username: name of the user who is being queried

        :response: * img_ids - list of pins related to a given board
                   * board_info - relevant board information

        :to test: curl -d "username=olte" -d "board_name=Things to get" -d "csid_from_client=1" http://localhost:8080/api/image/query-board
        """
        request_data = web.input()
        save_api_request(request_data)

        username = request_data.get('username')
        if not username:
            return e_response('username is required', 400)
        board_name = request_data.get('board_name')
        if not board_name:
            return e_response('board_name is required', 400)

        csid_from_client = request_data.get("csid_from_client")
        csid_from_server = ""

        # Get user_id from username
        user = db.select('users', where='username=$username',
                         vars={'username': username}).list()

        if len(user) == 0:
            return e_response("Given user does not exist")
        user_id = user[0].get("id")


        # Get board by user_id and board_name
        board = db.select('boards',
                          where='user_id=$uid and LOWER(name) like $bname',
                          vars={'uid': user_id,
                                'bname': board_name.lower() + '%'}).list()
        if len(board) == 0:
            return e_response("Impossible to find board %s for user %s" % (board_name, username), 404)
        # Get pins by board.id
        image_ids = db.select('pins', where='board_id=$bid',
                              vars={'bid': board[0]['id']},
                              what='id')
        return api_response(data={
                            'img_ids': [img["id"] for img in image_ids.list()],
                            'board': board
                            },
                            csid_from_server=csid_from_server,
                            csid_from_client=csid_from_client)


class ImageQuery(BaseAPI):
    """
    Image query for getting information about image

    method need some actual "logintoken" in security reason
    """
    def POST(self):
        """
        You can tested it using:
        curl --data "csid_from_client=1&query_type=all&logintoken=2mwvVHVFga&
        query_params=840&query_params=841&&query_params=842"
        http://localhost:8080/api/image/query

        "image_url" in response related with "link" in pins table.
        """
        request_data = web.input(query_params=[],)
        save_api_request(request_data)

        csid_from_client = request_data.get("csid_from_client")
        csid_from_server = ""

        #query_type = request_data.get("query_type")
        query_params = map(str, request_data.get("query_params"))
        image_data_list = []
        if len(query_params) > 0:
            image_data_list = self.query_image(query_params)
            status = 200
            error_code = ''
        else:
            status = 400
            error_code = 'Empty query_params'

        return api_response({"image_data_list": image_data_list},
                            status=status,
                            error_code=error_code,
                            csid_from_client=csid_from_client,
                            csid_from_server=csid_from_server)

    def query_image(self, query_params):
        image_data_list = []

        where = 'pins.id in (%s)' % (','.join(query_params))
        query = '''
            select
                tags.tags, pins.*, categories.id as category,
                categories.name as cat_name, pictures.resized_url as user_pic,
                users.username as user_username, users.name as user_name,
                users.id as user_id,
                count(distinct p1) as repin_count,
                count(distinct l1) as like_count
            from pins
                left join tags on tags.pin_id = pins.id
                left join pins p1 on p1.repin = pins.id
                left join likes l1 on l1.pin_id = pins.id
                left join users on users.id = pins.user_id
                left join pictures on users.pic_id = pictures.id
                left join follows on follows.follow = users.id
                left join pins_categories on pins.id=pins_categories.pin_id
                left join categories
                on pins_categories.category_id = categories.id
            where %s
            group by tags.tags, categories.id, pins.id, users.id, pictures.id
            order by timestamp desc''' % (where)

        images = db.query(query)

        image_properties = None
        for image in images:
            if not image['id']:
                continue

            if not image_properties or image_properties['id'] != image['id']:
                if image_properties:
                    image_properties['tags'] = list(image_properties['tags'])
                image_properties = {
                    "id": image.get('id'),
                    "name": image.get('name'),
                    "description": image.get('description'),
                    "link": image.get('link'),
                    "timestamp": image.get('timestamp'),
                    "product_url": image.get('product_url'),
                    "price": str(image.get('price')),
                    "price_range": image.get('price_range'),
                    "board_id": image.get('board_id'),
                    "external_id": image.get('external_id'),
                    "repin": image.get('repin'),
                    "views": image.get('views'),
                    "image_url": image.get('image_url'),
                    "image_width": image.get('image_width'),
                    "image_height": image.get('image_height'),
                    "image_202_url": image.get('image_202_url'),
                    "image_202_height": image.get('image_202_height'),
                    "image_212_url": image.get('image_212_url'),
                    "image_212_height": image.get('image_212_height'),
                    "like_count": image.get('like_count'),
                    "repin_count": image.get('repin_count'),
                    "category": image.get('category'),
                    "cat_name": image.get('cat_name'),
                    "user_id": image.get('user_id'),
                    "user_pic": image.get('user_pic'),
                    "user_username": image.get('user_username'),
                    "user_name": image.get('user_name')
                }

                if image.get('tags'):
                    image_properties['tags'] = \
                        set(image.get('tags').split())
                else:
                    image_properties['tags'] = set()

                image_data_list.append(image_properties)
            elif image.get('tags'):
                image_properties['tags'].update(
                    image.get('tags').split())
        if image_properties:
            image_properties['tags'] = list(image_properties['tags'])
        return image_data_list


class ManageProperties(BaseAPI):
    """
    API method for changing pin properties
    """
    def POST(self):
        request_data = web.input(
            hash_tag_add_list=[],
            hash_tag_remove_list=[],
        )

        update_data = {}
        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        # Get data from request
        image_id = request_data.get("image_id")
        image_title = request_data.get("image_title")
        image_desc = request_data.get("image_desc")
        product_url = request_data.get("product_url")
        link = request_data.get("link")
        price_range = request_data.get("price_range")
        board_id = request_data.get("board_id")
        hash_tag_add_list = map(str,
                                request_data.get("hash_tag_add_list"))
        hash_tag_remove_list = map(str,
                                   request_data.get("hash_tag_remove_list"))

        csid_from_client = request_data.get('csid_from_client')
        logintoken = request_data.get('logintoken')
        user_status, user = self.authenticate_by_token(logintoken)

        if not image_id:
            status = 400
            error_code = "Invalid input data"

        data['image_id'] = image_id
        if image_title:
            update_data['name'] = image_title
            data['image_title'] = image_title
        if image_desc:
            update_data['description'] = image_desc
            data['image_desc'] = image_desc
        if product_url:
            update_data['product_url'] = product_url
            data['product_url'] = product_url
        if link:
            update_data['link'] = link
            data['link'] = link
        if price_range:
            update_data['price_range'] = price_range
            data['price_range'] = price_range
        if board_id:
            update_data['board_id'] = board_id
            data['board_id'] = board_id

        # User id contains error code
        if not user_status:
            return user

        csid_from_server = user['seriesid']

        tags = db.select('tags', where='pin_id = %s' % (image_id)).list()
        if len(tags) > 0:
            tags = tags[0]['tags'].split()
            tags = set(tags) - set(hash_tag_remove_list)
            tags = tags | set(hash_tag_add_list)
            tags = ' '.join(tags)

            db.update('tags', where='pin_id = %s' % (image_id),
                      tags=tags)
        else:
            tags = ' '.join(hash_tag_add_list)
            db.insert('tags', pin_id=image_id, tags=tags)

        if status == 200 and len(update_data) > 0:
            db.update('pins', where='id = %s' % (image_id),
                      **update_data)

            pins = db.select('pins', where='id = %s' % (image_id)).list()
            if len(pins) > 0:
                data['external_id'] = pins[0]['external_id']

        response = api_response(data=data,
                                status=status,
                                error_code=error_code,
                                csid_from_client=csid_from_client,
                                csid_from_server=csid_from_server)
        return response


class Categorize(BaseAPI):
    """
    API method for changing category of pin
    """
    def POST(self):
        request_data = web.input(
            category_id_list=[],
        )

        update_data = {}
        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        # Get data from request
        image_id = request_data.get("image_id")
        category_id_list = map(int,
                               request_data.get("category_id_list"))

        csid_from_client = request_data.get('csid_from_client')
        logintoken = request_data.get('logintoken')
        user_status, user = self.authenticate_by_token(logintoken)

        if not image_id:
            status = 400
            error_code = "Invalid input data"

        data['image_id'] = image_id

        # User id contains error code
        if not user_status:
            return user

        csid_from_server = user['seriesid']

        if status == 200:
            db.delete('pins_categories', where='pin_id = %s' % (image_id))
            for category_id in category_id_list:
                db.insert('pins_categories',
                          pin_id=image_id,
                          category_id=category_id)

        response = api_response(data=data,
                                status=status,
                                error_code=error_code,
                                csid_from_client=csid_from_client,
                                csid_from_server=csid_from_server)
        return response


class QueryCategory(BaseAPI):
    """
    API for receiving pins by category
    """
    def POST(self):
        request_data = web.input(
            category_id_list=[],
        )

        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        # Get data from request
        query_type = request_data.get("query_type")
        category_id_list = map(str,
                               request_data.get("category_id_list"))
        page = request_data.get("page")
        items_per_page = request_data.get("items_per_page")
        not_private = request_data.get("not_private", False)

        csid_from_client = request_data.get('csid_from_client')
        csid_from_server = ""

        if query_type == "all" or not query_type:
            data = self.get_all(category_id_list, not_private)

        elif query_type == "new":
            data = self.get_new(category_id_list, not_private)

        elif query_type == "range":
            data = self.get_range(category_id_list,
                                  page,
                                  items_per_page,
                                  not_private)

        response = api_response(data=data,
                                status=status,
                                error_code=error_code,
                                csid_from_client=csid_from_client,
                                csid_from_server=csid_from_server)
        return response

    def get_all(self, category_id_list, not_private):
        data = {}
        image_id_list = []

        where = "random() < 0.1"
        if len(category_id_list) > 0:
            where = "pins_categories.category_id in (%s)" % \
                ','.join(category_id_list)

        if not_private:
            where = where + " AND not users.private"

        pins = db.query("SELECT * FROM pins \
                        JOIN pins_categories \
                        ON pins_categories.pin_id = pins.id \
                        LEFT JOIN users ON pins.user_id = users.id \
                        WHERE %s \
                        ORDER BY pins.timestamp desc" % (where))\
            .list()

        for pin in pins:
            if pin['pin_id'] not in image_id_list:
                image_id_list.append(pin['pin_id'])

        data['image_id_list'] = image_id_list

        return data

    def get_new(self, category_id_list, not_private):
        data = {}
        image_id_list = []
        timestamp_with_delta = int(
            (
                datetime.datetime.utcnow() -
                datetime.timedelta(days=settings.PIN_NEW_DAYS)
            )
            .strftime("%s")
        )

        where = "random() < 0.1"
        if len(category_id_list) > 0:
            where = "pins_categories.category_id in (%s)" % \
                ','.join(category_id_list)

        if not_private:
            where = where + " AND not users.private"

        pins = db.query("SELECT * FROM pins \
                        JOIN pins_categories \
                        ON pins_categories.pin_id = pins.id \
                        LEFT JOIN users ON pins.user_id = users.id \
                        WHERE %s and \
                        pins.timestamp >= %d \
                        ORDER BY pins.timestamp desc" %
                        (where, timestamp_with_delta))\
            .list()

        for pin in pins:
            if pin['pin_id'] not in image_id_list:
                image_id_list.append(pin['pin_id'])

        data['image_id_list'] = image_id_list

        return data

    def get_range(self, category_id_list, page, items_per_page, not_private):
        data = {}
        image_id_list = []

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

        where = "random() < 0.1"
        if len(category_id_list) > 0:
            where = "pins_categories.category_id in (%s)" % \
                ','.join(category_id_list)

        if not_private:
            where = where + " AND not users.private"

        pins = db.query("SELECT * FROM pins \
                        JOIN pins_categories \
                        ON pins_categories.pin_id = pins.id \
                        LEFT JOIN users ON pins.user_id = users.id \
                        WHERE %s \
                        ORDER BY random()" % (where))\
            .list()

        for pin in pins:
            if pin['pin_id'] not in image_id_list:
                image_id_list.append(pin['pin_id'])

        data['pages_count'] = math.ceil(float(len(image_id_list)) /
                                        float(items_per_page))
        data['pages_count'] = int(data['pages_count'])
        data['page'] = page
        data['items_per_page'] = items_per_page

        start = (page-1) * items_per_page
        end = start + items_per_page
        data['image_id_list'] = image_id_list[start:end]

        return data


class QueryHashtags(BaseAPI):
    """
    API method for get hashtags of pin
    """
    def POST(self):
        request_data = web.input()

        update_data = {}
        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        # Get data from request
        image_id = request_data.get("image_id")

        csid_from_client = request_data.get('csid_from_client')
        logintoken = request_data.get('logintoken')
        user_status, user = self.authenticate_by_token(logintoken)

        if not image_id:
            status = 400
            error_code = "Invalid input data"

        data['image_id'] = image_id

        # User id contains error code
        if not user_status:
            return user

        csid_from_server = user['seriesid']

        if status == 200:
            tags = db.select('tags', where='pin_id = %s' % (image_id)).list()
            if len(tags) > 0:
                tags = tags[0]['tags'].split()
            else:
                tags = []

            data['hashtag_list'] = tags

        response = api_response(data=data,
                                status=status,
                                error_code=error_code,
                                csid_from_client=csid_from_client,
                                csid_from_server=csid_from_server)
        return response


class QueryGetByHashtags(BaseAPI):
    """
    API for receiving pins by hashtag
    """
    def POST(self):
        request_data = web.input(
        )

        data = {}
        status = 200
        csid_from_server = None
        error_code = ""

        # Get data from request
        hashtag = request_data.get("hashtag", None)
        page = request_data.get("page")
        items_per_page = request_data.get("items_per_page", 10)
        not_private = request_data.get("not_private", False)

        csid_from_client = request_data.get('csid_from_client')
        csid_from_server = ""

        if not hashtag:
            return e_response('hashtag is required', 400)
        return api_response(self.get_range(hashtag, page, items_per_page, not_private),
                            status=status,
                            error_code=error_code,
                            csid_from_client=csid_from_client,
                            csid_from_server=csid_from_server)

    def get_range(self, hashtag, page, items_per_page, not_private):
        data = {}
        image_id_list = []

        if page:
            page = int(page)
            if page < 1:
                page = 1

        if not items_per_page:
            items_per_page = 10
            if items_per_page < 1:
                items_per_page = 1
        else:
            items_per_page = int(items_per_page)

        where = "random() < 0.1"
        if hashtag:
            where = "tags.tags LiKE '%%%s%%'" % \
                hashtag

        if not_private:
            where = where + " AND not users.private"

        pins = db.query("SELECT * FROM pins \
                        JOIN tags \
                        ON tags.pin_id = pins.id \
                        LEFT JOIN users ON pins.user_id = users.id \
                        WHERE %s \
                        ORDER BY pins.timestamp desc" % (where))\
            .list()

        for pin in pins:
            if hashtag and hashtag not in pin['tags'].split():
                continue

            if pin['pin_id'] not in image_id_list:
                image_id_list.append(pin['pin_id'])

        if page:
            data['pages_count'] = math.ceil(float(len(image_id_list)) /
                                            float(items_per_page))
            data['pages_count'] = int(data['pages_count'])
            data['page'] = page
            data['items_per_page'] = items_per_page

            start = (page-1) * items_per_page
            end = start + items_per_page
            data['image_id_list'] = image_id_list[start:end]
        else:
            data['image_id_list'] = image_id_list

        return data


def _generate_external_id():
    id = _new_external_id()
    while _already_exists(id):
        id = _new_external_id()
    return id


def _new_external_id():
    digits_and_letters = random.sample(DIGITS_AND_LETTERS, 9)
    return ''.join(digits_and_letters)


def _already_exists(id):
    db = database.get_db()
    results = db.where('pins', external_id=id)
    for _ in results:
        return True
    return False


class FollowOrUnfollowBoard(BaseAPI):
    """
    Allows to follow a given board if it was not already followed,
    Removes follow in case follow was set before.
    Works as toggle on/off

    :link: /api/image/follow-board
    """
    def POST(self):
        """
        :param str board_id: id of the board to follow
        :param str csid_from_client: CSID from client
        :param str user_id: id of the user who follows the board

        :response data: returns status:ok
        :example usage: curl --data "csid_from_client=1&user_id=98&board_id=15" http://localhost:8080/api/image/follow-board
        """
        request_data = web.input()
        csid_from_client = request_data.get('csid_from_client')
        user_id = request_data.get('user_id')
        board_id = request_data.get('board_id')
        try:
            db.insert('boards_followers', follower_id=user_id,
                      board_id=board_id)
            data = "Following"
        except Exception:
            db.delete('boards_followers',
                      where="follower_id=$uid and board_id=$bid",
                      vars={'uid': user_id, 'bid': board_id})
            data = "Follow"
        return api_response(data=data,
                            csid_from_client=csid_from_client,
                            csid_from_server="")
