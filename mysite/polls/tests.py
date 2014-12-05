from django.test import TestCase
from django.utils import timezone
import datetime
from polls.models import Question
from django.core.urlresolvers import reverse


class QuestionMethodTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was published recently should return False for questions whose
        pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=25)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_new_question(self):
        time = timezone.now() - datetime.timedelta(hours=5)
        new_question = Question(pub_date=time)
        self.assertEqual(new_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Creates a question with the given 'question_text' published by the
    given number of 'days' offset to now (negative for questions published
    in the past, positive for questions yet to be published
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions(self):
        """
        Even if no questions exist, an apropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are availible.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        """
        Question with a pub_date in past that should be displayed on the
        index page
        """
        create_question(question_text="Past question.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_with_a_future_question(self):
        """
        Questions with a pub date in the future should not be displayed.
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, 'No polls are availible.',
                            status_code=200)
        self.assertQuerysetEqual(
            response.context['latest_question_list'], []
        )

    def test_index_view_with_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        should be displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )
