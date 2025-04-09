from django.urls import path
from .views import (
    student_dashboard,
    instructor_dashboard,
    secretary_dashboard,
    admin_dashboard,
    dashboard_view,
    signup_view,
    profile_view,
    manage_accounts_view,
    manage_secretaries_view,
    AccountListView,
    AccountCreateView,
    AccountUpdateView,
    AccountDeleteView,
    create_account_and_send_email
)

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('signup/', signup_view, name='signup'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('instructor-dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('secretary-dashboard/', secretary_dashboard, name='secretary_dashboard'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('manage_accounts/', AccountListView.as_view(), name='account_list'),
    path('manage_accounts/create/', AccountCreateView.as_view(), name='account_create'),
    path('manage_accounts/<int:pk>/update/', AccountUpdateView.as_view(), name='account_update'),
    path('manage_accounts/<int:pk>/delete/', AccountDeleteView.as_view(), name='account_delete'),
    path('manage_secretaries/', manage_secretaries_view, name='manage_secretaries'),
    path('create_account_email/', create_account_and_send_email, name='create_account_email'),
]
