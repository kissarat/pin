from mypinnings.api import api_request, convert_to_id, convert_to_logintoken
from mypinnings import pin_utils

all_categories = None


def initialize(db):
    global all_categories
    # all_categories = list(db.select('categories', order='position desc, name',
    #                                 where='parent is null'))

    all_categories = []


def get_categories():
    global all_categories
    data = api_request("api/categories/get", "POST", {})
    if data['status'] == 200:
        all_categories = data['data']['categories_list']

    return all_categories


def get_categories_with_children(db):
    results = db.query('''
        select cat.id, cat.name, sub.id as subcategory_id, sub.name as subcatetory_name, sub.is_default_sub_category
        from categories cat
            left join categories sub on cat.id = sub.parent
        where cat.parent is null
        order by cat.name, sub.is_default_sub_category, sub.name
        ''')
    categories = []
    current_category = None
    for row in results:
        if not current_category or current_category['id'] != row.id:
            current_category = {'id': row.id,
                                'name': row.name,
                                'subcategories': []}
            categories.append(current_category)
        if row.subcategory_id:
            subcat = {'id': row.subcategory_id,
                      'name': row.subcatetory_name,
                      'id_default_sub_category': row.is_default_sub_category}
            current_category['subcategories'].append(subcat)
    return categories
