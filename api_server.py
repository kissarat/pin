#!/usr/bin/env python
import web

import api.views.base
import api.views.notifications
import api.views.signup
import api.views.images
import api.views.profile
import api.views.social
import api.views.search
import api.views.categories
import api.views.websearch
from api.utils import e_response
from mypinnings.database import load_sqla


class redirect:
    """
    Find and redirect to existed controller with '/' or without it
    """

    def GET(self, path):
        web.seeother('/' + path)


urls = (
    "/(.*)/", 'redirect',  # Handle urls with slash and without it
    "/query/notification", api.views.notifications.Notification,  # API handler for notifications
    "/notification/add", api.views.notifications.CreateNotification,
    "/notification/(?P<notification_id>\d+)", api.views.notifications.GetNotification,

    # API to user signup: authenticate user
    "/auth", api.views.signup.Auth,

    # API to user signup: register user
    "/signup/register", api.views.signup.Register,

    # API to user signup: confirmation user email
    "/signup/confirmuser", api.views.signup.ConfirmUser,
    "/signup/resend_activation", api.views.signup.ResendActivation,

    # API to upload images
    "/image/upload", api.views.images.ImageUpload,
    "/image/query-board", api.views.images.QueryBoardInfo,
    "/image/query", api.views.images.ImageQuery,
    "/image/mp", api.views.images.ManageProperties,
    "/image/categorize", api.views.images.Categorize,
    "/image/query/category", api.views.images.QueryCategory,
    "/image/query/hashtags", api.views.images.QueryHashtags,
    "/image/follow-board", api.views.images.FollowOrUnfollowBoard,
    "/image/query/get_by_hashtags", api.views.images.QueryGetByHashtags,

    # API to user profile: manage user products
    "/profile/mgl", api.views.profile.ManageGetList,
    "/profile/userinfo/update", api.views.profile.UserInfoUpdate,
    "/profile/userinfo/get", api.views.profile.GetProfileInfo,
    "/profile/userinfo/info", api.views.profile.ProfileInfo,
    "/profile/userinfo/set_privacy", api.views.profile.SetPrivacy,
    "/profile/updateviews/(?P<profile>\w+)", api.views.profile.UpdateProfileViews,
    "/profile/userinfo/boards", api.views.profile.QueryBoards,
    "/profile/userinfo/pins", api.views.profile.QueryPins,
    "/profile/test-username", api.views.profile.TestUsernameOrEmail,
    "/profile/userinfo/upload_pic", api.views.profile.PicUpload,
    "/profile/userinfo/upload_bg", api.views.profile.BgUpload,
    "/profile/userinfo/get_pictures", api.views.profile.GetPictures,
    "/profile/userinfo/remove_pic", api.views.profile.PictureRemove,
    "/profile/userinfo/album_default_picture", api.views.profile.AlbumDefaultPic,

    # API to user profile: change user password
    "/profile/pwd", api.views.profile.ChangePassword,

    # API for social networks: posting on user page
    "/social/poup", api.views.social.PostingOnUserPage,
    "/social/query/(followed-by|following)", api.views.social.QueryFollows,
    "/social/message", api.views.social.SocialMessage,
    "/social/message_to_conversation", api.views.social.SocialMessageToConversation,
    "/social/query/messages", api.views.social.SocialQueryMessages,
    "/social/query/conversations", api.views.social.SocialQueryConversations,
    "/social/picture/add_comment", api.views.social.AddCommentToPicture,
    "/social/picture/like_dislike", api.views.social.LikeDislikePicture,
    "/social/pin/like-unlike", api.views.social.LikeOrUnlikePin,

    # API for search: items and users
    "/search/items", api.views.search.SearchItems,
    "/search/people", api.views.search.SearchPeople,
    "/search/suggest", api.views.search.SearchSuggestions,

    # API for categories: get categories list
    "/categories/get", api.views.categories.GetCategories,

    # API for Web search: images
    "/websearch/images", api.views.websearch.Image
)
web.config.debug = True


def check_global_params(handler):
    req = web.input(
        project_id='1.0',
        format_type='JSON',
        os_type='web')
    if '1.0' != req.get('project_id'):
        return e_response('project_id must be 1.0', 400)
    if 'JSON' != req.get('format_type'):
        return e_response('Server supports JSON format_type only', 400)
    if req.get('os_type') not in ['web', 'ios', 'android', 'other']:
        return e_response('os_type can be web|ios|android|other only', 400)
    # try:
    return handler()
    # except Exception as ex:
    #     return e_response('Unhandled exception! ' + ex.message)


api_app = web.application(urls, globals(), autoreload=True)
api_app.add_processor(load_sqla)
api_app.add_processor(check_global_params)

if '__main__' == __name__:
    api_app.run()
