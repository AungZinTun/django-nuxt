from django.urls import include, path

from . import routers, views

urlpatterns = [
    path('data/', views.UserRetrieveUpdateDestroyAPIView.as_view(),
         name='user-data'),  # get data for the currently logged in user
    path('users/', include(routers.router.urls)),  # provides a few default
    # views that we can use for our CRUD operations.
]
