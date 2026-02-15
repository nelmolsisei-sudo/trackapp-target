"""trackapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('load_spreadsheet', views.load_spreadsheet, name="load_spreadsheet"),
    path("", views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('register', views.register, name="register"),
    path("user_list", views.user_list, name="user_list"), 
    path('profile/<int:user_id>', views.profile, name="profile"),
    path('meets', views.meets, name="meets"),
    path('meet/<int:meet_id>/<slug:name>/', views.meet, name="meet"),
    path('events', views.events, name="events"),
    path('event/<int:event_id>', views.event, name="event"),
    path('merge_event/<int:event_id>', views.merge_event, name="merge_event"),
    path('add_result/<int:user_id>', views.add_result, name="add_result"),
    path('edit_profile/<int:user_id>', views.edit_profile, name="edit_profile"),
    path('edit_result/<int:result_id>', views.edit_result, name="edit_result"),
    path('search', views.search, name="search"),
    path('merge_athlete/<int:user_id>', views.merge_athlete, name="merge_athlete"),
    path('delete_result/<int:result_id>', views.delete_result, name="delete_result"),
    path('create_season_goal/<int:user_id>', views.create_season_goal, name="create_season_goal"),
    path('remove_season_goal/<int:goal_id>', views.remove_season_goal, name="remove_season_goal"),
    path('merge_meet/<int:meet_id>', views.merge_meet, name="merge_meet"),
    path('teams', views.teams, name="teams"),
    path('team/<int:team_id>', views.team, name="team"),
    path('create_team/', views.edit_team, name="create_team"),
    path('edit_team/<int:team_id>', views.edit_team, name="edit_team"),
    path('debug_page', views.debug_page, name="debug_page"),
    path('add_coach/<int:team_id>', views.add_coach, name="add_coach"),
    path('remove_coach/<int:coach_id>/<int:team_id>', views.remove_coach, name="remove_coach"),
    path('add_athlete_to_team/<int:team_id>', views.add_athlete_to_team, name="add_athlete_to_team"),
    path('remove_athlete_from_team/<int:athlete_id>/<int:team_id>', views.remove_athlete_from_team, name="remove_athlete_from_team"),

    # Qualifying Times
    path('qualifying_levels',
        views.qualifying_levels,
        name="qualifying_levels"),
    path('create_qualifying_level/',
        views.edit_qualifying_level,
        name="create_qualifying_level"),
    path('edit_qualifying_level/<int:qualifying_level_id>',
        views.edit_qualifying_level,
        name="edit_qualifying_level"),
    path('load_qualifying_levels',
        views.load_qualifying_levels,
        name="load_qualifying_levels"),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
