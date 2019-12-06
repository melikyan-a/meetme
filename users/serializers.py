from rest_framework import serializers
from activity.models import Activity, UserActivity
from event.models import Event, UserEvent
from django.utils.translation import ugettext_lazy as _
from users.models import LikeUser, DislikeUser
from django.contrib.auth import get_user_model
UserModel = get_user_model()


# User social
class SocialTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)


class MeetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar', 'email',)


class UserLikemeSerializer(serializers.Serializer):

    def likedActivities(self, ActiveUserActivities: list, CurrentUserActivities: list) -> bool:
        if len([like for like in ActiveUserActivities if like in CurrentUserActivities]) > 0:
            return True
        return False

    def likedEvents(self, ActiveUserEvents: list, CurrentUserEvents: list) -> bool:
        if len([like for like in ActiveUserEvents if like in CurrentUserEvents]) > 0:
            return True
        return False

    def DislikedUser(self, ActiveDislikedUser: list, CurrentDislikedUser: int) -> bool:
        if CurrentDislikedUser in ActiveDislikedUser:
            return False
        return True

    def LikedUser(self, ActiveLikedUser: list, CurrentLikedUser: int) -> bool:
        if CurrentLikedUser in ActiveLikedUser:
            return False
        return True

    def do_user_resp(self, users):
        user = self.context['request'].user
        actList = [a['liked_activities'] for a in UserActivity.objects.filter(owner=user).values('liked_activities')]
        evList = [a['liked_events'] for a in UserEvent.objects.filter(owner=user).values('liked_events')]
        likedList = [a['liked'] for a in LikeUser.objects.filter(owner=user).values('liked')]
        dislikedList = [a['disliked'] for a in DislikeUser.objects.filter(owner=user).values('disliked')]
        resp = []
        for u in users:
            ulike = [a['liked_activities'] for a in UserActivity.objects.filter(owner=u).values('liked_activities')]
            uevent = [a['liked_events'] for a in UserEvent.objects.filter(owner=u).values('liked_events')]
            activity = self.likedActivities(ulike, actList)
            events = self.likedEvents(uevent, evList)
            liked = self.LikedUser(likedList, u.id)
            disliked = self.DislikedUser(dislikedList, u.id)
            if liked and disliked and activity or events:
                item = {
                    'id': u.pk,
                    'name': u.username,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'email': u.email,
                    'avatar': u.get_avatar(),
                }
                resp.append(item)

        resp_out = {
            'users': resp
        }
        return resp_out

    def get_result(self):
        result = self.do_user_resp(UserModel.objects.all().exclude(pk=self.context['request'].user.id))
        return result


class EventLikeSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)

    def get_result(self):
        eid = self.validated_data['event_id']
        try:
            Event.objects.get(pk=eid)
        except Event.DoesNotExist:
            return {'message': _('Event that you tried to like does not exists')}
        obj, created = UserEvent.objects.get_or_create(owner=self.context['request'].user)
        if eid in [a['id'] for a in obj.liked_events.all().values('id')]:
            obj.liked_events.remove(eid)
        else:
            obj.liked_events.add(eid)
        return {'message': _('ok')}


class ActivityLikeSerializer(serializers.Serializer):
    activity_id = serializers.IntegerField(required=True)

    def get_result(self):
        aid = self.validated_data['activity_id']
        try:
            Activity.objects.get(pk=aid)
        except Activity.DoesNotExist:
            return {'message': _('Activity that you tried to like does not exists')}
        obj, created = UserActivity.objects.get_or_create(owner=self.context['request'].user)
        if aid in [a['id'] for a in obj.liked_activities.all().values('id')]:
            obj.liked_activities.remove(aid)
        else:
            obj.liked_activities.add(aid)
        return {'message': _('ok')}


class EASerializer(serializers.Serializer):

    def do_activity_resp(self, activities):
        likeList = [a['liked_activities'] for a in UserActivity.objects.filter(owner=self.context['request'].user).values('liked_activities')]
        resp = []
        for a in activities:
            if bool(a.pk in likeList):
                continue
            item = {
                'id': a.pk,
                'name': a.name,
                'cat': a.category.name,
                'image': a.get_image(),
                "like": False,
            }
            resp.append(item)
        return resp

    def do_event_resp(self, events):
        likeList = [a['liked_events'] for a in UserEvent.objects.filter(owner=self.context['request'].user).values('liked_events')]
        resp = []
        for e in events:
            if bool(e.pk in likeList):
                continue
            item = {
                'id': e.pk,
                'name': e.name,
                'cat': e.category.name,
                'dt': e.dt,
                'image': e.get_image(),
                'like': False
            }
            resp.append(item)
        return resp

    def get_result(self, like=None):

        result = {}

        result['events'] = self.do_event_resp(Event.current_events.all())
        if like:
            result['activities'] = self.do_activity_like(Activity.current_activities.all())
        elif like is False:
            result['activities'] = self.do_activity_dislike(Activity.current_activities.all())
        elif like is None:
            result['activities'] = self.do_activity_resp(Activity.current_activities.all())
        return result


class UserCrossLikedSerializer(serializers.Serializer):

    def CrossLikedUser(self, ActiveCrossLikedUser: list, CurrentCrossLikedUser: list, CurrentlikedUser: int) -> bool:
        if len([like for like in ActiveCrossLikedUser if like == self.context['request'].user.id]) > 0 \
                and len([like for like in CurrentCrossLikedUser if like == CurrentlikedUser]) > 0:
            return True
        return False

    def do_user_resp(self, users):
        user = self.context['request'].user
        likedList = [a['liked'] for a in LikeUser.objects.filter(owner=user).values('liked')]
        resp = []
        for u in users:
            crossuliked = [a['liked'] for a in LikeUser.objects.filter(owner=u).values('liked')]
            crossliked = self.CrossLikedUser(crossuliked, likedList, u.id)
            if crossliked:
                item = {
                    'id': u.pk,
                    'name': u.username,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'email': u.email,
                    'avatar': u.get_avatar(),
                }
                resp.append(item)

        resp_out = {
            'users': resp
        }
        return resp_out

    def get_result(self):
        result = self.do_user_resp(UserModel.objects.all().exclude(pk=self.context['request'].user.id))
        return result


class UserLikedSerializer(serializers.Serializer):

    def LikedUser(self, ActiveLikedUser: list, CurrentLikedUser: int) -> bool:
        if CurrentLikedUser in ActiveLikedUser:
            return True
        return False

    def do_user_resp(self, users):
        user = self.context['request'].user
        likedList = [a['liked'] for a in LikeUser.objects.filter(owner=user).values('liked')]
        resp = []
        for u in users:
            liked = self.LikedUser(likedList, u.id)
            if liked:
                item = {
                    'id': u.pk,
                    'name': u.username,
                    'first_name': u.first_name,
                    'last_name': u.last_name,
                    'email': u.email,
                    'avatar': u.get_avatar(),
                }
                resp.append(item)

        resp_out = {
            'users': resp
        }
        return resp_out

    def get_result(self):
        result = self.do_user_resp(UserModel.objects.all().exclude(pk=self.context['request'].user.id))
        return result


class UserSympSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def get_result(self):
        uid = self.validated_data['user_id']
        try:
            UserModel.objects.get(pk=uid)
        except UserModel.DoesNotExist:
            return {'message': _('User that you tried to like does not exists')}
        obj, created = LikeUser.objects.get_or_create(owner=self.context['request'].user)
        if uid in [a['id'] for a in obj.liked.all().values('id')]:
            obj.liked.remove(uid)
        else:
            obj.liked.add(uid)
        return {'message': _('ok')}


class UserHateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def get_result(self):
        uid = self.validated_data['user_id']
        try:
            UserModel.objects.get(pk=uid)
        except UserModel.DoesNotExist:
            return {'message': _('User that you tried to dislike does not exists')}
        obj, created = DislikeUser.objects.get_or_create(owner=self.context['request'].user)
        if uid in [a['id'] for a in obj.disliked.all().values('id')]:
            obj.disliked.remove(uid)
        else:
            obj.disliked.add(uid)
        return {'message': _('ok')}

