from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.firstpage, name='firstpage'),
    path('review_web/', views.review_web, name='review_web'),

    path('login/', views.loginPage, name='login'),
    path('signup/', views.signupPage, name='signup'),
    path('logout/', views.logoutUser, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('categories/<str:category_id>/', views.books_by_category, name='books_by_category'),
    path('see-all/<str:section>/', views.see_all_view, name='see_all'),
    path('search/', views.search_books, name='search_books'),
    path('base-user/', views.base_user, name='base_user'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='libraria/password_reset.html'), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='libraria/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='libraria/password_reset_form.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='libraria/password_reset_done.html'), name='password_reset_complete'),
    path('change_password/', views.change_password, name='change_password'),

    path('admin/', views.admin, name='admin'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('editProfile/', views.editProfile, name='editProfile'),
    path('completeProfile/', views.completeProfile, name='completeProfile'),
    
    path('requests/', views.request_book, name='request'),
    path('accept/<str:pk>/', views.accept_borrow, name='accept_borrow'),
    path('decline/<str:pk>/', views.decline_borrow, name='decline_borrow'),
    path('validate-fine/<str:borrowing_id>/', views.validate_fine, name='validate_fine'),
    path('librender/', views.librender, name='librender'),
    path('list/', views.list_view, name='list_view'),
    path('delete/<str:pk>/', views.delete_borrowing, name='delete_borrowing'),
    path('addbook/', views.addbook, name='addbook'),
    path('editbook/<str:book_id>/', views.editbook, name='editbook'),
    path('deletebook/<str:book_id>/', views.deletebook, name='deletebook'),

    path('peminjaman/<str:book_id>/', views.halamanpinjam, name='halamanpinjam'),
    path('rakpinjam/', views.rak_pinjam, name='rak_pinjam'),
    path('borrow/<str:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<str:borrowing_id>/', views.return_book, name='return_book'),
    path('reviewuser/<str:book_id>/', views.review_user_view, name='review_user'),
    path('reviewbook/<str:book_id>/', views.review_book_view, name='review_book'),

    # path('resetPassword/', views.resetPassword, name='resetPassword'),
    # path('verificationCode/', views.verificationCode, name='verificationCode'),
    # path('newPassword/', views.newPassword, name='newPassword'),
]