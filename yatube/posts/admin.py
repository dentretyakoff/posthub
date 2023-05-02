from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    search_fields = ('slug',)
    empty_value_display = '-пусто-'


# При регистрации моделей Post и Group источником конфигурации для них
# назначаем классы PostAdmin и GroupAdmin
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
