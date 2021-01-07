from django.conf import settings
from django.db import models
# Create your models here.
from django.utils.text import slugify

from core.models import BaseAppModel, BaseVoteModel
from subq.models import SubQ


class Question(BaseAppModel):
    slug = models.SlugField(max_length=80, unique=True)
    post_title = models.CharField(max_length=100, blank=True, null=False, db_index=True)
    post_body = models.TextField(blank=True, null=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        blank=True,
        null=False,
        related_name="asked_questions",
    )
    subq = models.ForeignKey(
        SubQ, models.DO_NOTHING, blank=True, null=False, related_name="subq_questions"
    )

    class Meta:
        db_table = "question"
        verbose_name = "Question"

    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.post_title)
        return super(Question, self).save(*args, **kwargs)

    def archive(self):
        self.status = True
        self.save()


class QuestionWatchers(BaseAppModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=True,
        on_delete=models.CASCADE,
        related_name="watched_questions",
    )
    question = models.ForeignKey(
        Question, null=False, blank=True, on_delete=models.CASCADE, related_name="watchers"
    )

    class Meta:
        db_table = "question_watchers"
        verbose_name = "Question Watcher"


class QuestionViews(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="viewed_questions"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_views")

    class Meta:
        db_table = "question_views"
        verbose_name = "Question View"


class QTag(BaseAppModel):
    tag_name = models.CharField(max_length=50, unique=True, null=False, blank=True, db_index=True)
    slug = models.CharField(max_length=80, unique=True, null=False, blank=True)

    class Meta:
        db_table = "q_tag"
        verbose_name = "Question Tag"

    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.tag_name)
        return super(QTag, self).save(*args, **kwargs)


class QuestionQtag(BaseAppModel):
    qtag = models.ForeignKey(QTag, models.DO_NOTHING, null=False, related_name="question_tags")
    question = models.ForeignKey(Question, models.DO_NOTHING, related_name="question_tags")

    class Meta:
        db_table = "question_qtag"
        unique_together = (("question", "qtag"),)
        verbose_name = "Question QTags (Joined)"


class Reply(BaseAppModel):
    reply_body = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="question_replies",
    )
    question = models.ForeignKey(
        Question, models.DO_NOTHING, blank=True, null=True, related_name="question_replies"
    )

    class Meta:
        db_table = "reply"
        verbose_name = "Reply"

    def archive(self):
        self.status = True
        self.save()


class Comment(BaseAppModel):
    comment_body = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.DO_NOTHING, blank=True, null=True, related_name="comments"
    )
    question = models.ForeignKey(
        Question, models.DO_NOTHING, blank=True, null=True, related_name="question_comments"
    )
    reply = models.ForeignKey(
        Reply, models.DO_NOTHING, blank=True, null=True, related_name="reply_comments"
    )

    class Meta:
        db_table = "comment"
        verbose_name = "Comment"

    def archive(self):
        self.status = True
        self.save()


class CommentVote(BaseVoteModel):
    comment = models.ForeignKey(
        Comment, models.DO_NOTHING, blank=True, null=False, related_name="comment_votes"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="comment_votes",
    )

    class Meta:
        db_table = "comment_vote"
        verbose_name = "Comment Vote"


class QuestionVote(BaseVoteModel):
    question = models.ForeignKey(
        Question, models.DO_NOTHING, blank=True, null=False, related_name="question_votes"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="question_votes",
    )

    class Meta:
        db_table = "question_vote"
        verbose_name = "Question Vote"


class ReplyVote(BaseVoteModel):
    reply = models.ForeignKey(
        Reply, models.DO_NOTHING, blank=True, null=False, related_name="reply_votes"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="reply_votes",
    )

    class Meta:
        db_table = "reply_vote"
        verbose_name = "Reply Vote"
