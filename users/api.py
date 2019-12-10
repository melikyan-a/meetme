from .serializers import SocialTokenSerializer, ChangePasswordSerializer, MeetUserSerializer, EASerializer, \
    EventLikeSerializer, ActivityLikeSerializer, UserLikemeSerializer, UserCrossLikedSerializer, \
    UserLikedSerializer, UserSympSerializer, UserHateSerializer
from rest_framework.generics import get_object_or_404, UpdateAPIView, RetrieveUpdateAPIView
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
UserModel = get_user_model()
# from django.contrib.auth import login
from social_django.utils import psa
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
import requests
import json
from django.core import files
from io import BytesIO


@csrf_exempt
@api_view(['POST'])
@psa('social:complete')
def register_by_access_token(request, backend):
    serializer = SocialTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    access_token = request.data.get('access_token')
    provider = request.backend.name
    try:
        user = request.backend.do_auth(access_token)
    except Exception:
        return Response({"message": "The access token could not be decrypted"}, status=status.HTTP_400_BAD_REQUEST)
    if user:
        auth_token = Token.objects.get(user=user)
        if 'facebook' in provider:
            uid = json.loads(requests.get('https://graph.facebook.com/v3.2/me?access_token={}'.format(access_token)).text)
            if 'id' in uid:
                url = (
                    'http://graph.facebook.com/{0}/picture?type=large'
                ).format(uid['id'])
                resp = requests.get(url)
                fp = BytesIO()
                fp.write(resp.content)
                user.avatar.save('photo.jpg', files.File(fp))
        else:
            pass
        return Response({'token': '{}'.format(auth_token)}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Some error'}, status=status.HTTP_404_NOT_FOUND)


# Get user auth token
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = Token.objects.get(user=user)
        return Response({
            'id': user.pk,
            'token': token.key,
            'name': user.username,
            'avatar': user.avatar.url
        })


class MeetUserProfile(RetrieveUpdateAPIView):

    queryset = UserModel.objects.all()
    serializer_class = MeetUserSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'patch']

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        return obj


class ChangePasswordView(UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = UserModel
    permission_classes = (IsAuthenticated,)
    http_method_names = ['put']

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({'message': _('Success')}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EAViewSet(viewsets.GenericViewSet):

    serializer_classes = {
        'user_likeme_list': UserLikemeSerializer,
        'event_like': EventLikeSerializer,
        'activity_like': ActivityLikeSerializer,
        'get_actual_ea_list': EASerializer,
    }

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def user_likeme_list(self, request, *args, **kwargs):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def event_like(self, request, *args, **kwargs):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def activity_like(self, request, *args, **kwargs):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def get_actual_ea_list(self, request, *args, **kwargs):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    def get_result(self, request, like=None, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if like is None:
            result = serializer.get_result()
        else:
            result = serializer.get_result(like)
        return result

    def get_serializer(self, *args, **kwargs):
        serializer_class = kwargs.pop('serializer_class', None)
        if serializer_class is None:
            serializer_class = self.serializer_classes[self.action]
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class UserRelationViewSet(viewsets.GenericViewSet):
    serializer_classes = {
        'user_positive_list': UserLikedSerializer,
        'user_cross_positive_list': UserCrossLikedSerializer,
        'user_symp': UserSympSerializer,
        'user_hate': UserHateSerializer,
    }

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def user_positive_list(self, request):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def user_cross_positive_list(self, request):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def user_symp(self, request):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def user_hate(self, request):
        result = self.get_result(request)
        return Response(result, status=status.HTTP_200_OK)

    def get_result(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.get_result()
        return result

    def get_serializer(self, *args, **kwargs):
        serializer_class = kwargs.pop('serializer_class', None)
        if serializer_class is None:
            serializer_class = self.serializer_classes[self.action]
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
