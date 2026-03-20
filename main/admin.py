from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User, UserMedia, Action, Report

admin.site.unregister(Group)


class UserMediaInline(admin.TabularInline):
    model = UserMedia
    extra = 1
    fields = ('media_id', 'media_type')
    verbose_name = "Media"
    verbose_name_plural = "Media (Telegram File ID)"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'name', 'age', 'gender', 'is_verified', 'is_blocked', 'created_at')

    list_display_links = ('id', 'telegram_id')

    list_filter = ('gender', 'is_verified', 'is_blocked', 'age', 'created_at')

    search_fields = ('telegram_id', 'username', 'name')

    list_editable = ('is_verified', 'is_blocked')

    inlines = [UserMediaInline]

    fieldsets = (
        ('Main information', {
            'fields': ('telegram_id', 'username', 'name', 'age', 'bio', 'gender', 'search_gender')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_verified', 'is_blocked')
        }),
        ('Geolocation', {
            'fields': ('lat', 'long'),
            'classes': ('collapse',),
        }),
        ('Date information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'action_type', 'is_matched', 'created_at')
    list_filter = ('action_type', 'is_matched', 'created_at')
    search_fields = ('from_user__name', 'to_user__name', 'from_user__telegram_id')
    readonly_fields = ('from_user', 'to_user', 'created_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at', 'short_text')
    list_filter = ('created_at',)
    search_fields = ('from_user__name', 'to_user__name', 'text')
    readonly_fields = ('from_user', 'to_user', 'created_at', 'image_id')

    def short_text(self, obj):
        if obj.text and len(obj.text) > 50:
            return obj.text[:50] + '...'
        return obj.text or " "

    short_text.short_description = "Текст жалобы"

# @admin.register(UserImage)
# class UserImageAdmin(admin.ModelAdmin):
#     list_display = ('user', 'image_id')
#     search_fields = ('user__name', 'image_id')