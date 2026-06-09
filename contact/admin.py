from django.contrib import admin
from contact import models
from django.utils.html import format_html

# Register your models here.
@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display       = 'id', 'first_name', 'last_name', 'phone', 'photo', 'show',
    ordering           = '-id',
    list_filter        = 'created_date',
    search_fields      = 'id', 'first_name', 'last_name', 'show',
    list_per_page      = 10
    list_max_show_all  = 200
    list_editable      = 'first_name', 'last_name',
    list_display_links = 'id', 'phone',

    readonly_fields = ('photo',)

    def photo(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 50%;" />',
                obj.picture.url
            )
        return '-'
    
    photo.short_description = 'Foto'
            
@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name',
    ordering     = '-id',
