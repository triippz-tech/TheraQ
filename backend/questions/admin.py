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
    search_fields = ("user__username", "user__email", "question__post_title", "question__slug",)


class QTagAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "tag_name")
    list_filter = ("status",)
    search_fields = ("slug", "tag_name")
    ordering = ("tag_name",)


class QuestionQtagAdmin(admin.ModelAdmin):
    list_display = ("id", "qtag", "question")
    list_filter = ("status",)
    search_fields = ("qtag__tag_name", "qtag__slug", "question__post_tile", "question__slug", "slug", "tag_name")
    ordering = ("qtag__tag_name", "question__post_title")


class ReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "user")
    list_filter = ("status",)
    search_fields = ("question__post_tile", "question__slug", "user__username", "user__email", "reply_body")
    ordering = ("question__post_title",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "reply", "user")
    list_filter = ("status",)
    search_fields = ("question__post_tile", "question__slug", "user__username", "user__email", "comment_body")
    ordering = ("user__email",)


class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "vote_type", "comment", "user")
    list_filter = ("status", "vote_type")
    search_fields = ("user__username", "user__email", "comment__comment_body")
    ordering = ("comment__user__email",)


class QuestionVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "vote_type", "question", "user")
    list_filter = ("status", "vote_type")
    search_fields = ("user__username", "user__email", "question__slug", "question__post_title")
    ordering = ("question__post_title",)


class ReplyVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "vote_type", "reply", "user")
    list_filter = ("status", "vote_type")
    search_fields = ("user__username", "user__email",)
    ordering = ("reply__question",)


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
