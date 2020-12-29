from django.contrib import admin


# Register your models here.
from questions.models import Question, QuestionWatchers, QuestionViews, QuestionQtag, QTag, Reply, Comment, CommentVote, \
    QuestionVote, ReplyVote


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "post_title", "subq", "user")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "subq__sub_name", "subq_slug", "slug", "post_title", "post_body")
    ordering = ("post_title",)


class QuestionWatchersAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question",)
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "question__post_title", "question__slug",)


class QuestionViewsAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question",)
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "question__post_title", "question__slug",)


class QTagAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "tag_name")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "slug", "tag_name")
    ordering = ("tag_name",)


class QuestionQtagAdmin(admin.ModelAdmin):
    pass


class ReplyAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


class CommentVoteAdmin(admin.ModelAdmin):
    pass


class QuestionVoteAdmin(admin.ModelAdmin):
    pass


class ReplyVoteAdmin(admin.ModelAdmin):
    pass


admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionWatchers, QuestionWatchersAdmin)
admin.site.register(QuestionViews, QuestionViewsAdmin)
admin.site.register(QuestionQtag, QuestionQtagAdmin)
admin.site.register(QTag, QTagAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentVote, CommentVoteAdmin)
admin.site.register(QuestionVote, QuestionVoteAdmin)
admin.site.register(ReplyVote, ReplyVoteAdmin)
