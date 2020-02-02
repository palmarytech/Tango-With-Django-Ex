from django.contrib import admin

# Register your models here.
from rango.models import Category, Page
from rango.models import UserProfile


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'url', 'views', 'last_visit')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'views', 'likes')
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

