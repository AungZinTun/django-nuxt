from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from . import serializers

CustomUser = get_user_model()


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    **GET:** List details for a ``CustomUser``.

    **PUT:** Update details of a ``CustomUser``.

    **DELETE:** Delete a specific ``CustomUser``.

    This view can be used to retrieve data for the current logged in user.
    """

    queryset = CustomUser.objects.all()
    serializer_class = serializers.CustomUserRetrieveSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
