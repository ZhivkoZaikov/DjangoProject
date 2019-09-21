from django.db import models
from django.urls import reverse
import uuid  #required for unique book instance
from django.contrib.auth.models import User
from datetime import date,datetime
from django.core.exceptions import ValidationError



class Genre(models.Model):
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)', unique=True)
    image = models.ImageField(upload_to='images/genres', null=True, blank=True)
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('genre-detail', args=[str(self.id)])


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 characters <a href="https://www.isbn-international.org/content/what-isbn" target="_blank">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    date_added = models.DateField(null=True, blank=True)

    published = models.DateTimeField()
    copies = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    # customize the column title by adding short_description attribute to the callable
    display_genre.short_description = 'Genre'

    # def latest_books(self):
    #     # p = self.objects.all().order_by('-date_added')[:3]
    #     return ', '.join(book.title for book in self.objects.all().order_by('-date_added'))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])



class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='unique ID for this book')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateTimeField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # def somefunction(self):
    #     # the_date = str(self.due_back.strftime("%B-%d-%Y"))
    #     the_date = str(self.due_back.date())
    #     return the_date
    # def somefunctiontime(self):
    #     the_date = str(date.today())
    #     return the_date
    #
    # def compare(self):
    #     the_date = str(self.due_back.date())
    #     the_date_time = str(date.today())
    #     return the_date > the_date_time
    @property
    def is_overdue(self):
        # if self.due_back and date.today().strftime('%B %d %Y') > self.due_back.strftime('%B %d %Y'):
        if self.due_back and date.today() > self.due_back.date():
            return True
        return False

    # to print the verbose of 'status' in your website you would need to use get_status_display
    # it comes from get_variable_display and substitute variable with the actual variable
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan' ),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Book availability')

    class Meta:
        ordering = ['book__title', '-due_back']
        # permissions - permission name and display value
        # this needs to be assigned to the desired group in the admin site
        permissions = (('can_mark_returned', 'Set book as returned'),)

    def __str__(self):
        return f'{self.id} ({self.book.title})'

class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    # set 'Died' as a verbose name
    date_of_death = models.DateField('Died', null=True, blank=True)
    image = models.ImageField(upload_to='images/authors/', null=True, blank=True)
    about_the_author = models.TextField(max_length=1000, null=True, blank=True)
    class Meta:
        ordering = ['last_name', 'first_name']

    # def clean(self):
    #     super(Author,self).clean()
    #     if Author.objects.filter(first_name__iexact=self.clean('first_name')).exists():
    #         if Author.objects.filter(last_name__iexact=self.clean('last_name')).exists():
    #             raise ValidationError('Author already exists!')

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'

    def get_name(self):
        return f'{self.last_name}, {self.first_name} '

class Language(models.Model):
    name = models.CharField(max_length=50, help_text='Enter the book language(e.g. Spanish, English, Chinese, etc)')

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    YEAR_IN_SCHOOL_CHOICES = [
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
    ]
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )

    def is_upperclass(self):
        return self.year_in_school in (self.JUNIOR, self.SENIOR)

    def __str__(self):
        return self.name
