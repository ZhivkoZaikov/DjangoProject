from django import forms
import datetime
from .models import BookInstance, Genre, Author, Language, Book
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

class RenewBookForm(forms.Form):
    renewal_date = forms.DateTimeField(help_text='Enter a date between today and four weeks forward(default is three weeks)')

    def clean_renewal_date(self):

        data = self.cleaned_data['renewal_date']

        # check if date is in the past
        if data.date() < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal is in the past!'))

        # check if date is more than four weeks in the future
        if data.date() > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal is more than four weeks ahead!'))

        return data

# create form using models.py form
# this would use the models declaration
class RenewBookModelForm(forms.ModelForm):

    # for custom field validation use the clean_field_name() pattern
    # for example the due_back validation should be:
    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        if data == None:
            return data

        if data.date() < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal is in the past!'))

        if data.date() > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal is more than four weeks ahead!'))

        return data

    def clean_status(self):
        status = self.cleaned_data['status']
        data = self.cleaned_data['due_back']
        borrower = self.cleaned_data['borrower']
        if data == None and status == 'o':
            raise ValidationError(_('Loaned books should have a valid date'))

        if data != None and status != 'o':
            raise ValidationError(_('Only loaned books should have valid date!'))

        if borrower == None and status == 'o' or status == 'r':
            raise ValidationError(_('Loaned/Reserved books should havea borrower!'))

        if borrower != None and status == 'm' or status == 'a':
            raise ValidationError(_('Only loaned and reserved books should have a borrower!'))
        return status



    class Meta:
        model = BookInstance
        fields = [ 'due_back', 'borrower', 'status']
        # models informatio could be extended by:
        labels = {'due_back': _('New renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}

class BookUpdateForm(forms.Form):
    title = forms.CharField()
    author = forms.ModelChoiceField(queryset=Author.objects.all())
    summary = forms.CharField(widget=forms.Textarea, help_text='Enter a brief description of the book')
    isbn = forms.IntegerField(help_text='13 characters <a href="https://www.isbn-international.org/content/what-isbn" target="_blank">ISBN number</a>')
    genre = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(), widget=forms.CheckboxSelectMultiple(), help_text='Select a genre for this book')
    language = forms.ModelChoiceField(queryset=Language.objects.all())
    date_added = forms.DateField( required=False)

    published = forms.DateTimeField()
    copies = forms.IntegerField()
    image = forms.ImageField(required=True)


class BookCreateForm(forms.Form):
    title = forms.CharField()
    author = forms.ModelChoiceField(queryset=Author.objects.all())
    summary = forms.CharField(widget=forms.Textarea, help_text='Enter a brief description of the book')
    isbn = forms.IntegerField(help_text='13 characters <a href="https://www.isbn-international.org/content/what-isbn" target="_blank">ISBN number</a>')
    genre = forms.ModelMultipleChoiceField(required=False, queryset=Genre.objects.all(), widget=forms.CheckboxSelectMultiple(), help_text='Select a genre for this book')
    language = forms.ModelChoiceField(queryset=Language.objects.all())
    date_added = forms.DateField( required=False)

    published = forms.DateTimeField()
    copies = forms.IntegerField()
    image = forms.ImageField(required=True)

class authorCreateForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField(required=False)
    # set 'Died' as a verbose name
    date_of_death = forms.DateField(required=False)
    image = forms.ImageField()
    about_the_author = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data=super(authorCreateForm, self).clean()
        first_name_form = cleaned_data.get('first_name')
        last_name_form = cleaned_data.get('last_name')
        about_the_author = cleaned_data.get('about_the_author')

        if about_the_author.length() > 1000:
            raise forms.ValidationError(f'Text should be less than 1000 characters. (currently about_the_author.length() chars. )')
        # for author_name in Author.objects.all():
        #     for author_last_name in Author.objects.all():
        #         if first_name_form == author_name.first_name and last_name_form == author_last_name.last_name:
        if Author.objects.filter(first_name__iexact=first_name_form).exists():
            if Author.objects.filter(last_name__iexact=last_name_form).exists():
                raise forms.ValidationError(_('Author already exists!'))
        else:
            return cleaned_data

class authorUpdateForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField(required=False)
    # set 'Died' as a verbose name
    date_of_death = forms.DateField(required=False)
    image = forms.ImageField()
    about_the_author = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data=super(authorUpdateForm, self).clean()
        first_name_form = cleaned_data.get('first_name')
        last_name_form = cleaned_data.get('last_name')
        # for author_name in Author.objects.all():
        #     for author_last_name in Author.objects.all():
        #         if first_name_form == author_name.first_name and last_name_form == author_last_name.last_name:
        if Author.objects.filter(first_name__iexact=first_name_form).exists():
            if Author.objects.filter(last_name__iexact=last_name_form).exists():
                raise forms.ValidationError(_('Author already exists!'))
        else:
            return cleaned_data

class genreUpdateForm(forms.Form):
    name = forms.CharField(label='New name')
    image = forms.ImageField(label='New Image', required=False)

class genreCreateForm(forms.Form):
    name = forms.CharField(label='New name')
    image = forms.ImageField(label='New Image', required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Genre.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('Genre already exists!')

        return name

class AuthorForm(forms.ModelForm):
    # def clean(self):
    #     super(AuthorForm,self).clean()
    #     if Author.objects.filter(first_name__iexact=self.cleaned_data['first_name'])==self.cleaned_data['first_name']:
    #         if Author.objects.filter(last_name__iexact=self.cleaned_data['first_name'])==self.cleaned_data['first_name']:
    #             raise forms.ValidationError(_('Author already exists!'))
    def clean(self):
        cleaned_data=super(AuthorForm, self).clean()
        first_name_form = cleaned_data.get('first_name')
        last_name_form = cleaned_data.get('last_name')
        date_of_birth = cleaned_data.get('date_of_birth')
        date_of_death = cleaned_data.get('date_of_death')


        if date_of_birth > datetime.date.today():
            raise forms.ValidationError('Invalid date! Date of birth cannot be in the future!')

        if date_of_birth > datetime.date.today() - relativedelta(years=18):
            raise forms.ValidationError('Invalid date! Author must be 18 years old or above!')

        if date_of_death != None:
            if date_of_death > datetime.date.today():
                 raise forms.ValidationError('Invalid date! Date of death cannot be in the future!')
        # for author_name in Author.objects.all():
        #     for author_last_name in Author.objects.all():
        #         if first_name_form == author_name.first_name and last_name_form == author_last_name.last_name:
        qs = Author.objects.filter(first_name__iexact=first_name_form)
        qs2 = Author.objects.filter(last_name__iexact=last_name_form)
        if self.instance.pk is not None:
            qs = qs.exclude(pk=self.instance.pk)
            qs2 = qs2.exclude(pk=self.instance.pk)

        if qs.exists():
            if qs2.exists():
                raise forms.ValidationError(_('Author already exists!'))

        # if Author.objects.filter(first_name__iexact=first_name_form).exists():
        #     if Author.objects.filter(last_name__iexact=last_name_form).exists():
        #         raise forms.ValidationError(_('Author already exists!'))


        else:
            return cleaned_data

    class Meta:
        model = Author
        fields = '__all__'

class BookForm(forms.ModelForm):

    def clean(self):
        cleaned_data=super(BookForm, self).clean()
        title = cleaned_data.get('title')
        isbn = cleaned_data.get('isbn')
        date_added = cleaned_data.get('date_added')
        published = cleaned_data.get('published')
        copies = cleaned_data.get('copies')
        image = cleaned_data.get('image')

        if image == None:
            raise forms.ValidationError('Please choose an image!')

        if copies < 0:
            raise forms.ValidationError('Book copies must be positive or 0')

        if date_added > datetime.date.today() or published.date() > datetime.date.today():
            raise forms.ValidationError('Invalid date! Date cannot be in the future!')

        if len(isbn) != 13:
            raise forms.ValidationError('ISBN should be a 13 characters long!')

        qs = Book.objects.filter(title__iexact=title)
        if self.instance.pk is not None:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Book already exists! You may need to add book instance instead!')
        # title
        # isbn
        # date_added
        # published
        # copies
        return cleaned_data

    class Meta:
        model = Book
        fields = '__all__'
