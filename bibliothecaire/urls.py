from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('members/', views.list_members, name='list_members'),
    path('members/create/', views.create_member, name='create_member'),
    path('members/update/<int:member_id>/', views.update_member, name='update_member'),
    path('members/delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('media/', views.list_media, name='list_media'),
    path('media/create/', views.create_media, name='create_media'),
    path('loan/create/', views.create_loan, name='create_loan'),
    path('loan/manage/<int:member_id>/', views.manage_loans, name='manage_loans'),
    path('loan/return/<int:loan_id>/', views.return_loan, name='return_loan'),
    path('reservation/create/', views.create_reservation, name='create_reservation'),
    path('reservation/manage/<int:member_id>/', views.manage_reservation, name='manage_reservation'),
    path('reservation/end/<int:reservation_id>/', views.end_reservation, name='end_reservation'),

]
