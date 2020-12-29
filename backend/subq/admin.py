from django.contrib import admin

from subq.models import SubQ, SubQFollower


class SubQAdmin(admin.ModelAdmin):
    list_display = ("id", "sub_name", "slug", "owner")
    list_filter = ("status",)
    search_fields = ("owner__username", "owner__email", "sub_name", "slug", "description")
    ordering = ("sub_name",)


class SubQFollowerAdmin(admin.ModelAdmin):
    list_display = ("id", "subq", "follower", "is_banned")
    list_filter = ("status", "is_banned")
    search_fields = ("follower__username", "follower__email", "subq__slug", "subq__sub_name", "subq__description")
    ordering = ("follower__email",)


admin.site.register(SubQ, SubQAdmin)
admin.site.register(SubQFollower, SubQFollowerAdmin)
