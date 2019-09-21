from django.contrib import admin
from .models import Author, Book, BookInstance, Genre, Language, Student
# Register your models here.

def loaned(modeladmin, request, queryset):
    queryset.update(status='o')
loaned.short_description = 'Loaned Book'

def available(modeladmin, request, queryset):
    queryset.update(status='a')
available.short_description = 'Available Book'

def maintenance(modeladmin, request, queryset):
    queryset.update(status='m')
maintenance.short_description = 'Maintenance Book'

def reserved(modeladmin, request, queryset):
    queryset.update(status='r')
reserved.short_description = 'Reserved Book'




@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    empty_value_display = 'unknown'
    list_display = ['book', 'id', 'borrower', 'status', 'due_back']  #add is_overdue at some point
    list_editable = ['borrower', 'due_back','status']
    list_filter = ['borrower', 'book__genre']
    actions = [loaned, available, maintenance, reserved]



# Adding the below rules and adding an inline in Books would allow us to
# modify book instances in the Book admin url
class BookInstanceInline(admin.TabularInline):
    model = BookInstance



@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'language', 'isbn', 'display_genre']
    list_editable = ['author', 'isbn']
    list_filter = ['copies']
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'genre', 'language')
        }),
        ('Advanced Options', {
            # 'classes': ('collapse',),
            'fields': ('summary', 'isbn', 'published', 'copies', 'image', 'date_added')
        }),
    )

    inlines = [BookInstanceInline]

class BookInline(admin.TabularInline):
    model = Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'image', ('date_of_birth', 'date_of_death'), 'about_the_author']

    inlines = [BookInline]

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Student)
admin.site.empty_value_display = 'Blank(no input)'
