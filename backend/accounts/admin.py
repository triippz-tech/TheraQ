from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from accounts.models import User, UserSetting, UserProfile, UserSchool, UserLicense, UserEmployer, UserCertification


class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "username", "created", "modified")
    list_filter = ("is_active", "is_staff", "groups")
    search_fields = ("email", "username")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "username", "password1", "password2")}),)


class UserSettingAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "user__email")
    ordering = ("user__email",)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "user__email")
    ordering = ("user__email",)


class UserCertificationAdmin(admin.ModelAdmin):
    list_display = ("id", "institution_name", "certificate_program", "certificate_number")
    search_fields = ("user__username", "user__email", "institution_name", "certificate_program", "certificate_number")
    ordering = ("certificate_program",)


class UserEmployerAdmin(admin.ModelAdmin):
    list_display = ("id", "employer_name", "position", "current_position")
    list_filter = ("current_position",)
    search_fields = ("user__username", "user__email", "position", "current_position")
    ordering = ("employer_name",)


class UserLicenseAdmin(admin.ModelAdmin):
    list_display = ("id", "issuing_authority", "license_type", "license_number")
    list_filter = ("completion_date", "expiration_date",)
    search_fields = ("user__username", "user__email", "issuing_authority", "license_type", "license_number")
    ordering = ("license_type",)


class UserSchoolAdmin(admin.ModelAdmin):
    list_display = ("id", "school_name", "program", "degree_type", "current_student")
    list_filter = ("current_student", "degree_type", "start_date", "graduate_date",)
    search_fields = ("user__username", "user__email", "school_name", "program", "degree_type", "current_student")
    ordering = ("school_name", "program")


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserSetting, UserSettingAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserSchool, UserSchoolAdmin)
admin.site.register(UserLicense, UserLicenseAdmin)
admin.site.register(UserEmployer, UserEmployerAdmin)
admin.site.register(UserCertification, UserCertificationAdmin)
