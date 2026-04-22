from django.contrib import admin
from .models import Profile, Course, Opportunity, Application, SavedOpportunity, SubAdmin


@admin.register(SubAdmin)
class SubAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'can_manage_users', 'can_manage_opportunities', 'can_manage_courses', 'assigned_by', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__email')


admin.site.register(Profile)
admin.site.register(Course)
admin.site.register(Opportunity)
admin.site.register(Application)
admin.site.register(SavedOpportunity)
