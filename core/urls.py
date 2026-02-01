from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:profile_id>/join/', views.join_profile, name='join_profile'),
    path('profile/<int:profile_id>/', views.profile_home, name='profile_home'),
    path('profile/<int:profile_id>/upload/image/', views.upload_image_card, name='upload_image_card'),
    path('profile/<int:profile_id>/upload/prompt/', views.upload_prompt_card, name='upload_prompt_card'),
    path('profile/<int:profile_id>/rank/<str:card_type>/', views.rank_cards, name='rank_cards'),
    path('profile/<int:profile_id>/stats/', views.stats, name='stats'),
    path('profile/<int:profile_id>/results/', views.final_results, name='final_results'),
    path('profile/<int:profile_id>/dashboard/', views.live_dashboard, name='live_dashboard'),
    path('profile/<int:profile_id>/dashboard/data/', views.live_dashboard_data, name='live_dashboard_data'),
    path('profile/<int:profile_id>/dashboard/chart-data/', views.live_dashboard_chart_data, name='live_dashboard_chart_data'),
]
