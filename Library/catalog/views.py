from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Book, BookInstance, Author, Language, Genre
from num2words import num2words
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import random, datetime
from django_random_queryset import RandomManager
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import RenewBookForm, RenewBookModelForm, BookUpdateForm, BookCreateForm, authorCreateForm, \
    genreCreateForm, genreUpdateForm, authorUpdateForm, AuthorForm, BookForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ValidationError




def index(request):
    num_books = num2words(Book.objects.all().count())
    num_instances = num2words(BookInstance.objects.all().count())
    num_authors = num2words(Author.objects.count())
    num_instances_available = num2words(BookInstance.objects.filter(status__exact = 'a').count())
    books = Book.objects.all()[:12]
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_authors': num_authors,
        'num_instances_available': num_instances_available,
        'books': books,
        'num_visits': num_visits,
    }
    return render(request, 'catalog/index.html', context=context)

def booklist(request):
    book_list = Book.objects.all()

    paginator = Paginator(book_list, 3)
    page = request.GET.get('page', 1)

    try:
        my_book_list = paginator.page(page)
    except PageNotAnInteger:
        my_book_list = paginator.page(1)
    except EmptyPage:
        my_book_list = paginator.page(paginator.num_pages)


    latest_books = Book.objects.all().order_by('-date_added')[:3]
    return render(request, 'catalog/book_list.html', {'my_book_list': my_book_list, 'latest_books': latest_books})



def BookDetailView(request, id):
   book = get_object_or_404(Book, id=id)
   # you can use {% for copy in book.bookinstance_set.all %} or filter or other func
   # instead of the code below
   instances = BookInstance.objects.filter(book__title__icontains=book.title)
   number_of_instances = instances.count()
   available_books = BookInstance.objects.filter(book__title__icontains=book.title).filter(status='a').count()
   return render(request, 'catalog/book_detail.html', {'book': book, 'number_of_instances': number_of_instances,
                                                       'available_books': available_books, 'instances': instances})

def authorList(request):
    authors = Author.objects.all()
    authors_count = num2words(authors.count())
    return render(request, 'catalog/author_list.html',{'authors': authors, "authors_count":authors_count})

# class AuthorDetailView(generic.DetailView):
#     model = Author

def AuthorDetailView(request, id):
    # context = Author.objects.filter(id=id)
    author = get_object_or_404(Author, id=id)
    # context = {'object': obj}
    author_books = Book.objects.filter(author__first_name=author.first_name)
    return render(request, 'catalog/author_detail.html', {'author':author, 'author_books': author_books})

def genreView(request):
    genre = Genre.objects.all()

    return render(request, 'catalog/genre_list.html', {'genre': genre})

def genreDetail(request, id):
    genre = get_object_or_404(Genre, id=id)
    return render(request, 'catalog/genre_detail.html', {'genre': genre})

@login_required
def LoanedBookByUser(request):
    loaned_books = BookInstance.objects.filter(borrower=request.user)
    return render(request, 'catalog/bookinstance_list_borrowed_user.html', {'loaned_books': loaned_books})

@staff_member_required
def allBorrowedBooks(request):
    loaned_books = BookInstance.objects.filter(status__exact='o').order_by('due_back')
    paginator = Paginator(loaned_books, 4)
    page = request.GET.get('page', 1)

    try:
        my_book_list = paginator.page(page)
    except PageNotAnInteger:
        my_book_list = paginator.page(1)
    except EmptyPage:
        my_book_list = paginator.page(paginator.num_pages)
    return render(request, 'catalog/allborrowedbooks.html', {'loaned_books': loaned_books, 'my_book_list': my_book_list})

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # this would return to the 'all-borrowed' URL
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date':proposed_renewal_date})

    context = {'form': form, 'book_instance': book_instance}

    return render(request, 'catalog/book_renew_librarian.html', context)

@permission_required('catalog.can_mark_returned')
def renew_book_model_form(request, pk):
    # book_instance = RenewBookModelForm(request.POST)
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)

        if form.is_valid():
            book_instance.due_back=form.cleaned_data['due_back']
            book_instance.borrower=form.cleaned_data['borrower']
            book_instance.status=form.cleaned_data['status']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {'form': form, 'book_instance': book_instance}

    return render(request, 'catalog/book_model_renew_librarian.html', context)

@staff_member_required
def updateBookForm(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookUpdateForm(request.POST, request.FILES)

        if form.is_valid():
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.summary = form.cleaned_data['summary']
            book.isbn = form.cleaned_data['isbn']
            book.genre.set(form.cleaned_data['genre'])
            book.language = form.cleaned_data['language']
            book.date_added = form.cleaned_data['date_added']
            book.published = form.cleaned_data['published']
            book.copies = form.cleaned_data['copies']
            book.image = request.FILES['image']
            # request.FILES['image'] = book.image
            book.save()

            return HttpResponseRedirect(reverse('books'))

    else:
        genres = book.genre.all()
        form = BookUpdateForm(initial={ 'author': book.author, 'summary': book.summary, 'isbn': book.isbn,
                                       'language': book.language, 'date_added': book.date_added, 'published': book.published,
                                       'copies': book.copies, 'image': book.image, 'title': book.title,
                                        'genre': [x for x in book.genre.all()]})

    context = {'book': book, 'form': form}

    return render(request, 'catalog/book_update_form_custom.html', context)

# ====================================================================
#     if request.method == 'POST':
#         user_form = UserRegistrationForm(request.POST)
#
#         if user_form.is_valid():
#             new_user = user_form.save(commit=False)
#             # instead of using the raw password the user entered
#             # we use the set_password method to encrypt it
#             new_user.set_password = (user_form.cleaned_data['password'])
#             new_user.save()
#             profile = Profile.objects.create(user=new_user)
#             create_action(new_user, 'has create an account')
#             return render(request, 'account/register_done.html', {'new_user': new_user})
#     else:
#         user_form = UserRegistrationForm()
#     return render(request, 'account/register.html', {'user_form': user_form})
# ====================================================================

@staff_member_required
def createBookForm(request):
    book = Book()
    if request.method == 'POST':
        form = BookCreateForm(request.POST, request.FILES)

        if form.is_valid():

            # book.id = Book.objects.last()
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.summary = form.cleaned_data['summary']
            book.isbn = form.cleaned_data['isbn']
            # book.genre.set(x for x in form.cleaned_data['genre'])
            book.genre.set(form.cleaned_data['genre'])
            book.language = form.cleaned_data['language']
            book.date_added = form.cleaned_data['date_added']
            book.published = form.cleaned_data['published']
            book.copies = form.cleaned_data['copies']
            # book.image = request.FILES['image']
            request.FILES['image'] = book.image
            book.save()

            return HttpResponseRedirect(reverse('books'))

    else:
        form = BookCreateForm(initial={'title': 'title', 'date_added': '1940-12-31', 'published': '1940-12-31'})
        # genres = book.genre.all()
        # form = BookUpdateForm(initial={ 'author': book.author, 'summary': book.summary, 'isbn': book.isbn,
        #                                'language': book.language, 'date_added': book.date_added, 'published': book.published,
        #                                'copies': book.copies, 'image': book.image, 'title': book.title,
        #                                 'genre': [x for x in book.genre.all()]})

    context = {'form': form}

    return render(request, 'catalog/book_create_form_custom.html', context)

@staff_member_required
def authorCreate(request):
    author = Author()
    if request.method == 'POST':
        form = authorCreateForm(request.POST, request.FILES)
        if form.is_valid():
            author.first_name = form.cleaned_data['first_name']
            author.last_name = form.cleaned_data['last_name']
            author.date_of_birth = form.cleaned_data['date_of_birth']
            author.date_of_death = form.cleaned_data['date_of_death']
            author.image = request.FILES['image']
            author.about_the_author = form.cleaned_data['about_the_author']
            author.save()
            return HttpResponseRedirect(reverse('author_create_success'))
    else:
        form = authorCreateForm(initial={'date_of_birth': 'year-month-day'})

    return render(request, 'catalog/author_create.html', {'form': form})

def authorCreateSuccess(request):
    return render(request, 'catalog/authorCreateSuccess.html')

# By default the created/updated views will redirect to the newly modified page
# you can configure this by setting a 'success_url'

# create and update views use the same template named after the model name plus _form.html
# for example author_form.html(note - both create and update would use the template!)
# ===========================================================================================
# class BookCreate(PermissionRequiredMixin, CreateView):
#     permission_required = 'catalog.can_mark_returned'
#     model = Book
#     fields = '__all__'
#     initial = {'date_of_death': '05/01/2018'}

# class BookUpdate(PermissionRequiredMixin, UpdateView):
#     permission_required = 'catalog.can_mark_returned'
#     model = Book
#     fields = '__all__'
#     initial = {'date_of_death': '05/01/2018'}

# ==============================================================================



# class AuthorCreate(PermissionRequiredMixin, CreateView):
#     permission_required = 'catalog.can_mark_returned'
#     model = Author
#     fields = '__all__'
#     initial = {'date_of_death': '2018-01-22'}

class AuthorUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death','about_the_author','image']
    success_url = reverse_lazy('authors')
    form_class = AuthorForm
    # def clean(self):
    #     cleaned_data = super(AuthorUpdateView, self).clean()
    #     first_name_form = cleaned_data.get('first_name')
    #     last_name_form = cleaned_data.get('last_name')
    #     # for author_name in Author.objects.all():
    #     #     for author_last_name in Author.objects.all():
    #     #         if first_name_form == author_name.first_name and last_name_form == author_last_name.last_name:
    #     if Author.objects.filter(first_name__iexact=first_name_form).exists():
    #         if Author.objects.filter(last_name__iexact=last_name_form).exists():
    #             raise ValidationError('Author already exists!')
    #     else:
    #         return cleaned_data
# DeleteView requires to specify 'success_url'
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Author
    success_url = reverse_lazy('authors')

# ==============================================================================


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death','about_the_author','image']

# DeleteView requires to specify 'success_url'
class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    success_url = reverse_lazy('authors')
# ==============================================================================

@staff_member_required
def genreUpdateView(request, pk):
    genre = get_object_or_404(Genre, pk=pk)

    if request.method == 'POST':
        form = genreUpdateForm(request.POST, request.FILES)

        if form.is_valid():

            genre.name = form.cleaned_data['name']
            genre.image = request.FILES['image']
            genre.save()

            return HttpResponseRedirect(reverse('genre_update_success'))

    else:
        form = genreUpdateForm(initial={'name': genre.name, 'image': genre.image})

    context = {'form': form, 'genre': genre}

    return render(request, 'catalog/genre_update_form_custom.html', context)

def genreUpdateSuccessView(request):
    return render(request, 'catalog/genre_update_success.html')


class GenreDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
    model = Genre
    success_url = reverse_lazy('genre-removed')

def genreRemovedView(request):
    return render(request, 'catalog/genre_removed_success.html')

@staff_member_required
def genreCreateView(request):
    genre = Genre()
    if request.method == 'POST':
        form = genreCreateForm(request.POST, request.FILES)
        if form.is_valid():
            genre.name = form.cleaned_data['name']
            genre.image = request.FILES['image']
            genre.save()
            return HttpResponseRedirect(reverse('genre_create_success'))
    else:
        form = genreCreateForm()

    return render(request, 'catalog/genre_create.html', {'form': form})

def genreCreateSuccess(request):
    return render(request, 'catalog/genreCreateSuccess.html')

@staff_member_required
def overdueBookInstanceView(request):
    expired = [obj for obj in BookInstance.objects.all() if obj.is_overdue]

    return render(request, 'catalog/overdueBooks.html', {'expired': expired})

@staff_member_required()
def authorUpdateView(request, pk):
    author = get_object_or_404(Author, pk=pk)

    # authorUpdateForm

    if request.method == 'POST':
        form = authorUpdateForm(request.POST, request.FILES)

        if form.is_valid():

            author.first_name = form.cleaned_data['first_name']
            author.last_name = form.cleaned_data['last_name']
            author.date_of_birth = form.cleaned_data['date_of_birth']
            author.date_of_death = form.cleaned_data['date_of_death']
            author.image = request.FILES['image']
            author.about_the_author = form.cleaned_data['about_the_author']

            author.save()

            return HttpResponseRedirect(reverse('genre_update_success'))

    else:
        form = authorUpdateForm(initial={'first_name': author.first_name, 'last_name': author.last_name,
                                         'image': author.image, 'date_of_birth': author.date_of_birth,
                                         'date_of_death': author.date_of_death, 'about_the_author': author.about_the_author })

    context = {'form': form, 'genre': author}

    return render(request, 'catalog/author_update_form_custom.html', context)


class BookCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death','about_the_author','image']
    success_url = reverse_lazy('book-create-success')
    form_class = BookForm
    template_name_suffix = '_create_book'

def bookCreateSuccess(request):
    return render(request, 'catalog/book_create_success.html' )


class BookUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
    model = Book
    # fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death','about_the_author','image']
    success_url = reverse_lazy('book-update-success')
    form_class = BookForm
    template_name_suffix = '_update_book'

def bookUpdateSuccess(request):
    return render(request, 'catalog/book_update_success.html' )
