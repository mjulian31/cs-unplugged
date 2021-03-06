from tests.BaseTestWithDB import BaseTestWithDB
from django.urls import reverse


class TopicURLTest(BaseTestWithDB):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "en"

    def test_valid_topic(self):
        kwargs = {
            "topic_slug": "binary-numbers",
        }
        url = reverse("topics:topic", kwargs=kwargs)
        self.assertEqual(url, "/en/topics/binary-numbers/")
