""" Implements images part of the API """
import os
import web
import uuid
import datetime
import random
import string

from mypinnings import database
from api.views.base import BaseAPI, BaseQueryRange
from api.utils import e_response, authenticate
from mypinnings.conf import settings
from mypinnings.media import store_image_from_filename

DIGITS_AND_LETTERS = string.ascii_letters + string.digits


class ImageUpload(BaseAPI):
    """ Handles image upload and storing it on the file system """
    @authenticate
    def POST(self):
        """ Images upload main handler

        Can be tested using the following command:
        curl -F "image_title=some_title" -F "image_descr=some_descr" \
        -F "image_file=@/home/oleg/Desktop/hard.jpg" \
        http://localhost:8080/api/image/upload
        """
        request_data = web.input(image_file={})
        file_obj = request_data.get('image_file')

        # For some reason, FileStorage object treats itself as False
        if type(file_obj) == dict:
            return e_response("Required args are missing", 400)

        file_path = self.save_file(file_obj)
        images_dict = store_image_from_filename(self.db,
                                                file_path,
                                                widths=(202, 212))

        external_id = _generate_external_id()

        pin_id = self.create_db_record({
            'name': request_data.get("image_title"),
            'description': request_data.get("image_descr"),
            'user_id': self._user['id'],
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
            'image_212_height': images_dict[212]['height']
        })

        self.data['image_id'] = pin_id
        self.data['external_id'] = external_id
        return self.respond()

    def create_db_record(self, kwargs):
        """
        Creates image record in the database.
        """
        # Do not record empty fields
        kwargs = {key: value for (key, value) in kwargs.items()
                  if value is not None}
        return self.db.insert("pins", **kwargs)

    def save_file(self, file_obj, upload_dir=None):
        """
        Saves uploaded file to a given upload dir.
        """
        if not upload_dir:
            upload_dir = self.get_media_path()
        filename = file_obj.filename
        filename = self.get_file_name(filename, upload_dir)
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, 'w') as upload_file:
            upload_file.write(file_obj.file.read())
        return filepath

    @staticmethod
    def get_media_path():
        """
        Returns or creates media directory.
        """
        media_path = settings.MEDIA_PATH
        if not os.path.exists(media_path):
            os.makedirs(media_path)
        return media_path

    @staticmethod
    def get_file_name(filename, upload_dir):
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

        username = request_data.get('username')
        if not username:
            return e_response('username is required', 400)
        board_name = request_data.get('board_name')
        if not board_name:
            return e_response('board_name is required', 400)

        # Get user_id from username
        user = self.db.select(
            'users', where='username=$username',
            vars={'username': username})

        if len(user) == 0:
            return e_response("Given user does not exist")
        user_id = user[0].get("id")

        # Get board by user_id and board_name
        board = self.db.select(
            'boards', where='user_id=$uid and LOWER(name) like $bname',
            vars={'uid': user_id, 'bname': board_name.lower() + '%'}).list()
        if len(board) == 0:
            return e_response("There are no board %s for user %s" % (board_name, username), 404)
        # Get pins by board.id
        image_ids = self.db.select(
            'pins', where='board_id=$bid', vars={'bid': board[0]['id']}, what='id')
        self.data['img_ids'] = [img["id"] for img in image_ids.list()]
        self.data['board'] = board
        return self.respond()


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

        query_params = map(str, request_data.get("query_params"))
        self.data['image_data_list'] = []
        if len(query_params) > 0:
            self.data['image_data_list'] = self.query_image(query_params)
        else:
            return e_response('Empty query_params', 400)

        return self.respond()

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
            order by timestamp desc''' % where

        images = self.db.query(query)

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
    @authenticate
    def POST(self):
        request_data = web.input(
            hash_tag_add_list=[],
            hash_tag_remove_list=[],
        )

        update_data = {}

        # Get data from request
        image_id = request_data.get("image_id")
        if not image_id:
            return e_response('image_id is required', 400)
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

        self.data['image_id'] = image_id
        if image_title:
            update_data['name'] = image_title
            self.data['image_title'] = image_title
        if image_desc:
            update_data['description'] = image_desc
            self.data['image_desc'] = image_desc
        if product_url:
            update_data['product_url'] = product_url
            self.data['product_url'] = product_url
        if link:
            update_data['link'] = link
            self.data['link'] = link
        if price_range:
            update_data['price_range'] = price_range
            self.data['price_range'] = price_range
        if board_id:
            update_data['board_id'] = board_id
            self.data['board_id'] = board_id

        tags = self.db.select('tags', where='pin_id = %s' % image_id)
        if len(tags) > 0:
            tags = tags[0]['tags'].split()
            tags = set(tags) - set(hash_tag_remove_list)
            tags = tags | set(hash_tag_add_list)
            tags = ' '.join(tags)

            self.db.update('tags', where='pin_id = %s' % image_id,
                           tags=tags)
        else:
            tags = ' '.join(hash_tag_add_list)
            self.db.insert('tags', pin_id=image_id, tags=tags)

        if len(update_data) > 0:
            self.db.update('pins', where='id = %s' % image_id,
                           **update_data)

            pins = self.db.select('pins', where='id = %s' % image_id)
            if len(pins) > 0:
                self.data['external_id'] = pins[0]['external_id']
        return self.respond()


class Categorize(BaseAPI):
    """
    API method for changing category of pin
    """
    @authenticate
    def POST(self):
        request_data = web.input(category_id_list=[])

        # Get data from request
        image_id = request_data.get("image_id")
        if not image_id:
            return e_response('image_id is required', 400)
        category_id_list = map(int,
                               request_data.get("category_id_list"))

        self.data['image_id'] = image_id
        self.db.delete('pins_categories', where='pin_id = %s' % image_id)
        for category_id in category_id_list:
            self.db.insert('pins_categories', pin_id=image_id, category_id=category_id)
        return self.respond()


class PinsQueryRange(BaseQueryRange):
    def query(self):
        pins = BaseQueryRange.query(self)
        image_id_list = []
        for pin in pins:
            if pin['pin_id'] not in image_id_list:
                image_id_list.append(pin['pin_id'])
        self.data['image_id_list'] = image_id_list


class CategoryQueryRange(PinsQueryRange):
    def query(self):
            request_data = web.input(category_id_list=[], not_private=False)
            category_id_list = map(str,
                                   request_data.get("category_id_list"))
            not_private = request_data.get("not_private")
            if len(category_id_list) > 0:
                self.where.append("pins_categories.category_id in (%s)" % ','.join(category_id_list))
            else:
                self.where.append("random() < 0.1")
            if not_private:
                self.where.append("not users.private")
            PinsQueryRange.query(self)


class QueryCategory(CategoryQueryRange):
    """
    API for receiving pins by category
    """
    select = """SELECT * FROM pins
                JOIN pins_categories
                ON pins_categories.pin_id = pins.id
                LEFT JOIN users ON pins.user_id = users.id
                WHERE %s
                ORDER BY pins.timestamp desc"""

    def POST(self):
        request_data = web.input()

        # Get data from request
        query_type = request_data.get("query_type")

        if 'all' == query_type or not query_type:
            self.get_all()
        elif 'new' == query_type:
            self.get_new()
        elif 'range' == query_type:
            self.query_range()
        else:
            return e_response('Invalid query_type ' + query_type)
        return self.respond()

    def get_all(self):
        self.query()

    def get_new(self):
        timestamp_with_delta = int(
            (
                datetime.datetime.utcnow() -
                datetime.timedelta(days=settings.PIN_NEW_DAYS)
            )
            .strftime("%s")
        )
        self.where.append('timestamp_with_delta >= ' + str(timestamp_with_delta))
        self.query()


class QueryHashtags(BaseAPI):
    """
    API method for get hashtags of pin
    """
    @authenticate
    def POST(self):
        request_data = web.input()

        # Get data from request
        image_id = request_data.get("image_id")
        if not image_id:
            return e_response('image_id is required', 400)

        self.data['image_id'] = image_id
        tags = self.db.select('tags', where='pin_id = ' + image_id).list()
        if len(tags) > 0:
            tags = tags[0]['tags'].split()
        self.data['hashtag_list'] = tags

        return self.respond()


class QueryGetByHashtags(CategoryQueryRange):
    """
    API for receiving pins by hashtag
    """
    select = """SELECT * FROM pins
                JOIN tags
                ON tags.pin_id = pins.id
                LEFT JOIN users ON pins.user_id = users.id
                WHERE %s
                ORDER BY pins.timestamp desc"""

    def POST(self):
        request_data = web.input()

        # Get data from request
        hashtag = request_data.get("hashtag", None)
        if not hashtag:
            return e_response('hashtag is required', 400)
        self.where.append("tags.tags ILIKE '%%%s%%'" % hashtag)
        self.query_range()
        return self.respond()


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
        user_id = request_data.get('user_id')
        board_id = request_data.get('board_id')
        try:
            self.db.insert(
                'boards_followers', follower_id=user_id,
                board_id=board_id)
            self.data = "Following"
        except Exception:
            self.db.delete(
                'boards_followers', where="follower_id=$uid and board_id=$bid",
                vars={'uid': user_id, 'bid': board_id})
            self.data = "Follow"
        return self.respond()
