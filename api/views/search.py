import re
import web
import json

from api.views.base import BaseAPI, BaseQueryRange
from api.views.images import PinsQueryRange
from api.utils import e_response, authenticate


def make_tsquery(q):
    q = ''.join([x if x.isalnum() else ' ' for x in q])
    return re.sub(r' +', ' | ', q)


def search(self):
    # Get data from request
    query = web.input().get("query", None)
    if not query:
        return e_response('query is required', 400)
    query = make_tsquery(query)
    self.where.append(query)
    self.query_range()
    return self.respond()


class SearchItems(PinsQueryRange):
    """
    API for receiving pins ids by query
    """
    select = """
            select
                pins.id as pin_id,
                ts_rank_cd(to_tsvector(tags.tags), query) as rank1,
                ts_rank_cd(pins.tsv, query) as rank2
            from pins
                left join tags on tags.pin_id = pins.id
                join to_tsquery('%s') query on true
                left join users on users.id = pins.user_id
                left join categories on categories.id in
                    (select category_id from pins_categories
                    where pin_id = pins.id limit 1)
            where query @@ pins.tsv or query @@ to_tsvector(tags.tags)
            group by tags.tags, categories.id, pins.id, users.id, query.query
            order by rank1, rank2 desc"""

    def POST(self):
        return search(self)


class SearchPeople(BaseQueryRange):
    """
    API for receiving users by query
    """

    search = """
            select
                id, username, name,
                ts_rank_cd(users.tsv, query) as rank,
                count(distinct f1) <> 0 as is_following
            from users
                join to_tsquery('%s') query on true
                left join follows f1 on f1.follower = $user_id
                and f1.follow = users.id
            where query @@ users.tsv group by users.id, query.query
            order by rank desc"""

    @authenticate
    def POST(self):
        self.select_vars['user_id'] = self.user['id']
        return search(self)

    def query(self):
        self.data['users'] = BaseQueryRange.query(self)


class SearchSuggestions(BaseAPI):
    def GET(self):
        q = web.input().q
        #response = []
        if q:
            sql = 'select username, "name" from users where username ilike $q order by username asc limit 10'
            response = [[user.username, user.name] for user in self.db.query(sql, vars={'q': q + '%'})]
            sql = 'select string from queries where string ilike $q group by string limit 10'
            response += [query.string for query in self.db.query(sql, vars={'q': q + '%'})]
        else:
            sql = """select string from
                    (select string from queries order by "timestamp" desc) as t
                     group by string limit 20"""
            response = [query.string for query in self.db.query(sql)]
        return json.dumps(response)
