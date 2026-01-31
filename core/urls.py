from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/<int:profile_id>/', views.profile_home, name='profile_home'),
    path('profile/<int:profile_id>/upload/image/', views.upload_image_card, name='upload_image_card'),
    path('profile/<int:profile_id>/upload/prompt/', views.upload_prompt_card, name='upload_prompt_card'),
    path('profile/<int:profile_id>/rank/<str:card_type>/', views.rank_cards, name='rank_cards'),
]
