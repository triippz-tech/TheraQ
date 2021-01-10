import json

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from questions.models import (
    QTag,
    Question,
    QuestionVote,
    QuestionWatchers,
    Reply,
    ReplyVote,
    Comment,
    CommentVote
)
from subq.models import SubQ


User = get_user_model()


# Create your tests here.
def create_user(**params):
    """ Helper function to create new user """
    return User.objects.create_user(**params)


def create_normal_client():
    test_user = User.objects.create_user(
        username="test_user", password="testing", email="tester@tester.com"
    )
    client = APIClient()
    client.force_authenticate(user=test_user)
    return test_user, client


def create_super_client():
    super_user = User.objects.create_superuser(
        username="super_user", password="super_user_pass", email="super_user@tester.com"
    )
    client = APIClient()
    client.force_authenticate(user=super_user)
    return super_user, client


def create_subq(**params):
    return SubQ.objects.create(**params)


def create_question(**params):
    return Question.objects.create(**params)


# pylint: disable=too-many-ancestors, too-many-instance-attributes
class TestQuestionViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@user.com", password="user1pass")
        self.user2 = create_user(username="user2", email="user2@user.com", password="user2pass")
        self.user3 = create_user(username="user3", email="user3@user.com", password="user3pass")
        self.subq1 = create_subq(
            sub_name="sub1", description="SUB 1 Decsription", owner=self.test_user
        )
        self.subq2 = create_subq(
            sub_name="subq2", description="SUB 2 Decsription", owner=self.user1
        )
        self.question1 = create_question(
            slug="Sluggy",
            post_title="My Title",
            post_body="My Body",
            author=self.user1,
            subq=self.subq1,
        )
        self.question2 = create_question(
            slug="Sluggy2",
            post_title="My Title2",
            post_body="My Body",
            author=self.test_user,
            subq=self.subq1,
        )

    def test_create(self):
        tag1 = QTag.objects.create(tag_name="Early Intervention")
        tag2 = QTag.objects.create(tag_name="Late Intervention")
        payload = {
            "post_title": "How do i fix this kid?",
            "post_body": "Please fix this. What do i do? Seriously, help i am soooooooo lost!",
            "subq": {"id": self.subq1.pk},
            "qtags": [
                {"id": tag1.pk},
                {"id": tag2.pk}
            ]
        }

        res = self.normal_client.post(
            "/api/questions/question/", json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["post_title"], "How do i fix this kid?")
        self.assertEqual(
            res.data["post_body"],
            "Please fix this. What do i do? Seriously, help i am soooooooo lost!",
        )
        self.assertIsNotNone(res.data["slug"])
        self.assertEqual(res.data.get("author")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("subq")["id"], self.subq1.pk)
        self.assertEqual(len(res.data.get("question_tags")), 2)

    def test_list(self):
        res = self.normal_client.get("/api/questions/question/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Question.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        res = self.normal_client.get(f"/api/questions/question/?author__email={self.user1.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Question.objects.filter(author__email=self.user1.email).count(),
            len(res.data["results"]),
        )

        res = self.normal_client.get(
            f"/api/questions/question/?subq__sub_name={self.subq1.sub_name}"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Question.objects.filter(subq__sub_name=self.subq1.sub_name).count(),
            len(res.data["results"]),
        )

        res = self.normal_client.get(f"/api/questions/question/?slug={self.question1.slug}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Question.objects.filter(slug=self.question1.slug).count(), len(res.data["results"])
        )

    def test_retrieve(self):
        res = self.normal_client.get(f"/api/questions/question/{self.question1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.question1.id, res.data["id"])

        res = self.normal_client.get(f"/api/questions/question/{self.question2.slug}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.question2.slug, res.data["slug"])

    def test_delete(self):
        res = self.normal_client.delete(f"/api/questions/question/{self.question1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.normal_client.delete(f"/api/questions/question/{self.question2.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        question_refresh = Question.objects.get(pk=self.question2.pk)
        self.assertTrue(question_refresh.status)

    def test_add_watch(self):
        res = self.normal_client.post(f"/api/questions/question/{self.question1.pk}/add_watch/")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)

    def test_remove_watch(self):
        watcher = QuestionWatchers.objects.create(user=self.test_user, question=self.question1)
        res = self.normal_client.post(f"/api/questions/question/{watcher.pk}/remove_watch/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_vote(self):
        payload = {"vote_type": "DOWN_VOTE"}
        res = self.normal_client.post(
            f"/api/questions/question/{self.question1.pk}/add_vote/",
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_remove_vote(self):
        QuestionVote.objects.create(
            user=self.test_user, question=self.question1, vote_type="DOWN_VOTE"
        )
        res = self.normal_client.post(f"/api/questions/question/{self.question1.pk}/remove_vote/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_comment(self):
        payload = {"comment_body": "I am commenting on this non-sense"}
        res = self.normal_client.post(
            f"/api/questions/question/{self.question1.pk}/add_comment/", payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["comment_body"], "I am commenting on this non-sense")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("question")["id"], self.question1.pk)

    def test_add_reply(self):
        payload = {"reply_body": "Hey it's a comment!"}
        res = self.normal_client.post(
            f"/api/questions/question/{self.question1.pk}/add_reply/", payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("question")["id"], self.question1.pk)


class TestQTagViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()

    def test_create_tag(self):
        payload = {"tag_name": "Early Intervention"}
        res = self.normal_client.post(
            "/api/questions/qtag/", json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["tag_name"], "Early Intervention")
        self.assertIsNotNone(res.data["slug"])

    def test_retrieve_qtag(self):
        qtag = QTag.objects.create(tag_name="Early Intervention")
        res = self.normal_client.get(f"/api/questions/qtag/{qtag.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["tag_name"], "Early Intervention")
        self.assertIsNotNone(res.data["slug"])

    def test_list_qtag(self):
        QTag.objects.create(tag_name="Early Intervention")
        QTag.objects.create(tag_name="Late Intervention")
        res = self.normal_client.get("/api/questions/qtag/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(QTag.objects.all().count(), len(res.data["results"]))

    def test_list_filter_qtag(self):
        QTag.objects.create(tag_name="Early Intervention")
        QTag.objects.create(tag_name="Middle Intervention")
        QTag.objects.create(tag_name="Late Intervention")
        res = self.normal_client.get("/api/questions/qtag/?tag_name=Late Intervention")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            QTag.objects.filter(tag_name="Late Intervention").count(), len(res.data["results"])
        )


class TestReplyViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.user1 = create_user(username="user1", email="user1@user.com", password="user1pass")
        self.subq1 = create_subq(
            sub_name="subq1", description="SUB 1 Decsription", owner=self.test_user
        )
        self.question1 = create_question(
            slug="Sluggy",
            post_title="My Title",
            post_body="My Body",
            author=self.test_user,
            subq=self.subq1,
        )

    def test_create_reply(self):
        payload = {"reply_body": "This is my reply", "question": {"id": self.question1.pk}}
        res = self.normal_client.post(
            "/api/questions/reply/", json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["reply_body"], "This is my reply")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("question")["id"], self.question1.pk)

    def test_update_reply(self):
        reply = Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        payload = {"reply_body": "This is my new body"}
        res = self.normal_client.patch(
            f"/api/questions/reply/{reply.pk}/",
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["reply_body"], "This is my new body")

    def test_list_reply(self):
        Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        Reply.objects.create(
            question=self.question1, user=self.user1, reply_body="This is my Reply"
        )
        Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        res = self.normal_client.get("/api/questions/reply/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Reply.objects.all().count(), len(res.data["results"]))

    def test_retrieve_reply(self):
        Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        Reply.objects.create(
            question=self.question1, user=self.user1, reply_body="This is my Reply"
        )
        Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )

        res = self.normal_client.get(f"/api/questions/reply/?question__id={self.question1.pk}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Reply.objects.filter(question__id=self.question1.pk).count(), len(res.data["results"])
        )

        res = self.normal_client.get(f"/api/questions/reply/?user__email={self.user1.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Reply.objects.filter(user__email=self.user1.email).count(), len(res.data["results"])
        )

    def test_delete_reply(self):
        reply = Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        res = self.normal_client.delete(f"/api/questions/reply/{reply.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_vote(self):
        reply = Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        payload = {"vote_type": "DOWN_VOTE"}
        res = self.normal_client.post(
            f"/api/questions/reply/{reply.pk}/add_vote/",
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["vote_type"], "DOWN_VOTE")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("reply")["id"], reply.pk)

    def test_remove_vote(self):
        reply = Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )
        ReplyVote.objects.create(reply=reply, user=self.test_user, vote_type="DOWN_VOTE")
        res = self.normal_client.post(f"/api/questions/reply/{reply.pk}/remove_vote/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_add_comment(self):
        reply = Reply.objects.create(
            question=self.question1, user=self.test_user, reply_body="This is my Reply"
        )

        payload = {"comment_body": "I am commenting on this non-sense"}
        res = self.normal_client.post(f"/api/questions/reply/{reply.pk}/add_comment/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["comment_body"], "I am commenting on this non-sense")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("reply")["id"], reply.pk)


class TestQuestionCommentViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.user1 = create_user(username="user1", email="user1@user.com", password="user1pass")
        self.subq1 = create_subq(
            sub_name="subq1", description="SUB 1 Decsription", owner=self.test_user
        )
        self.question1 = create_question(
            slug="Sluggy",
            post_title="My Title",
            post_body="My Body",
            author=self.test_user,
            subq=self.subq1,
        )

    def test_create_q_comment(self):
        payload = {
            "comment_body": "I am here to comment on this mock comment.",
            "question": {
                "id": self.question1.pk
            }
        }

        res = self.normal_client.post("/api/questions/question-comment/", json.dumps(payload),
                                      content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["comment_body"], "I am here to comment on this mock comment.")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("question")["id"], self.question1.pk)

    def test_update_q_comment(self):
        qcomment = Comment.objects.create(user=self.test_user, question=self.question1, comment_body="Initial Body")
        payload = {
            "comment_body": "Updated Body"
        }
        res = self.normal_client.patch(f"/api/questions/question-comment/{qcomment.pk}/", json.dumps(payload),
                                       content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["comment_body"], "Updated Body")

    def test_destroy_q_comment(self):
        qcomment = Comment.objects.create(user=self.test_user, question=self.question1, comment_body="Initial Body")
        res = self.normal_client.delete(f"/api/questions/question-comment/{qcomment.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        refreshed = Comment.objects.get(pk=qcomment.pk)
        self.assertTrue(refreshed.status)

    def test_add_vote_q_comment(self):
        qcomment = Comment.objects.create(user=self.test_user, question=self.question1, comment_body="Initial Body")
        payload = {
            "vote_type": "DOWN_VOTE",
            "comment": {
                "id": qcomment.pk
            }
        }
        res = self.normal_client.post(
            f"/api/questions/question-comment/{qcomment.pk}/add_vote/",
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["vote_type"], "DOWN_VOTE")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("comment")["id"], qcomment.pk)

    def test_remove_vote_q_comment(self):
        qcomment = Comment.objects.create(user=self.test_user, question=self.question1, comment_body="Initial Body")
        CommentVote.objects.create(comment=qcomment, user=self.test_user, vote_type="DOWN_VOTE")
        res = self.normal_client.post(f"/api/questions/question-comment/{qcomment.pk}/remove_vote/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class TestReplyCommentViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.user1 = create_user(username="user1", email="user1@user.com", password="user1pass")
        self.subq1 = create_subq(
            sub_name="subq1", description="SUB 1 Decsription", owner=self.test_user
        )
        self.question1 = create_question(
            slug="Sluggy",
            post_title="My Title",
            post_body="My Body",
            author=self.test_user,
            subq=self.subq1,
        )

    def test_create_reply_comment(self):
        reply = Reply.objects.create(question=self.question1, user=self.test_user, reply_body="My Reply")
        payload = {
            "comment_body": "I am here to comment on this mock comment.",
            "reply": {
                "id": reply.pk
            }
        }

        res = self.normal_client.post("/api/questions/reply-comment/", json.dumps(payload),
                                      content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["comment_body"], "I am here to comment on this mock comment.")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("reply")["id"], reply.pk)

    def test_update_reply_comment(self):
        reply = Reply.objects.create(question=self.question1, user=self.test_user, reply_body="My Reply")
        rcomment = Comment.objects.create(user=self.test_user, reply=reply, comment_body="Initial Body")
        payload = {
            "comment_body": "Updated Body"
        }
        res = self.normal_client.patch(f"/api/questions/reply-comment/{rcomment.pk}/", json.dumps(payload),
                                       content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["comment_body"], "Updated Body")

    def test_delete_reply_comment(self):
        reply = Reply.objects.create(question=self.question1, user=self.test_user, reply_body="My Reply")
        rcomment = Comment.objects.create(user=self.test_user, reply=reply, comment_body="Initial Body")
        res = self.normal_client.delete(f"/api/questions/reply-comment/{rcomment.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        refreshed = Comment.objects.get(pk=rcomment.pk)
        self.assertTrue(refreshed.status)

    def test_add_vote_reply_comment(self):
        reply = Reply.objects.create(question=self.question1, user=self.test_user, reply_body="My Reply")
        rcomment = Comment.objects.create(user=self.test_user, reply=reply, comment_body="Initial Body")
        payload = {
            "vote_type": "DOWN_VOTE",
            "comment": {
                "id": rcomment.pk
            }
        }
        res = self.normal_client.post(
            f"/api/questions/reply-comment/{rcomment.pk}/add_vote/",
            json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["vote_type"], "DOWN_VOTE")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)
        self.assertEqual(res.data.get("comment")["id"], rcomment.pk)

    def test_remove_vote_reply_comment(self):
        reply = Reply.objects.create(question=self.question1, user=self.test_user, reply_body="My Reply")
        rcomment = Comment.objects.create(user=self.test_user, reply=reply, comment_body="Initial Body")
        CommentVote.objects.create(comment=rcomment, user=self.test_user, vote_type="DOWN_VOTE")
        res = self.normal_client.post(f"/api/questions/reply-comment/{rcomment.pk}/remove_vote/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class TestCommentVoteViewSet(APITestCase):
    def setUp(self):
        pass


class TestQuestionVoteViewSet(APITestCase):
    def setUp(self):
        pass


class TestReplyVoteViewSet(APITestCase):
    def setUp(self):
        pass
