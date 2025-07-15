from django.contrib import admin
from .models import ChatGroup, GroupMessage

@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'is_private', 'online_users_count')
    filter_horizontal = ('members',)  # Better UI for selecting members

    def online_users_count(self, obj):
        try:
            return obj.users_online.count()
        except AttributeError:
            return 0
    online_users_count.short_description = 'Online Users'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            # When creating a new ChatGroup, no users are selected by default
            form.base_fields['members'].initial = []
        return form

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'group', 'body', 'created_at')
    list_filter = ('group', 'author')
    search_fields = ('body', 'author__username', 'group__group_name')
