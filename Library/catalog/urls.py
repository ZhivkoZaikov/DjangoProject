from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),


    path('genres/', views.genreView, name='genres'),
    path('genres/<int:id>/', views.genreDetail, name='genre-detail'),
    path('genres/<int:pk>/update/', views.genreUpdateView, name='genre-update'),
    path('genres/update/success/', views.genreUpdateSuccessView, name='genre_update_success'),
    path('genres/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre-delete'),
    path('genres/delete/removed', views.genreRemovedView, name='genre-removed'),
    path('genres/create/', views.genreCreateView, name='genres-create'),
    path('genres/create/success/', views.genreCreateSuccess, name='genre_create_success'),

    # The <uuid:pk> pattern matches only if the primary key is a correctly formatted uuid
    path('books/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('books/<uuid:pk>/fullrenew/', views.renew_book_model_form, name='full-renew-book-librarian'),
    path('mybooks/', views.LoanedBookByUser, name='my-borrowed'),
    path('allborrowedbooks/', views.allBorrowedBooks, name='all-borrowed'),
    path('expiredBooks/', views.overdueBookInstanceView, name='expired-books'),

    path('books/', views.booklist, name='books'),
    path('books/<int:id>/', views.BookDetailView, name='book-detail'),
    # path('books/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/create/success/', views.bookCreateSuccess, name='book-create-success'),
    path('books/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update_custom'),
    path('books/update/success/', views.bookUpdateSuccess, name='book-update-success'),


    path('authors/', views.authorList, name='authors'),
    path('authors/<int:id>/', views.AuthorDetailView, name='author-detail'),
    path('authors/<int:pk>/update/', views.AuthorUpdateView.as_view(), name='author_update'),
    path('authors/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
    path('authors/create/', views.authorCreate, name='author_create'),
    path('authors/create-success/', views.authorCreateSuccess, name='author_create_success'),


]
