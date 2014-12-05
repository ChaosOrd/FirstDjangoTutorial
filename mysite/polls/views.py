from django.http import HttpResponseRedirect
from polls.models import Question
from polls.models import Choice
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Returns five last published questions (not including those to be
        published in the future)
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': 'You did not select any choice,',
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponceRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if
        # a user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
