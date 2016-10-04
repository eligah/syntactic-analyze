# coding:utf-8

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from django.utils.translation import ugettext as _
from django.views import generic

from simple.models import Simple


def index(request):
    sentence = _("Please Enter A Sentence:")
    return render(request, 'simple/index.html', context={'sentence': sentence})


def simple(request):
    return render(request, 'simple/demo.html')


def analysis(request):
    # get the sentence
    try:
        sentence = request.POST['input']
    except KeyError:
        return render(request, 'simple/index.html')

    print "Sentence: %s" % sentence

    m_sentence, created = Simple.objects.get_or_create(sentence_text=sentence)
    m_sentence.request_count += 1
    m_sentence.request_date = timezone.now()
    m_sentence.save()

    return HttpResponseRedirect(reverse('simple:results', args=(m_sentence.id,)))


class ResultView(generic.DetailView):
    model = Simple
    template_name = 'simple/results.html'

    def get_context_data(self, **kwargs):
        context = super(ResultView, self).get_context_data(**kwargs)
        return context


def feedback(request):
    try:
        sentence = request.POST['input']
    except KeyError:
        return render(request, 'simple/index.html')
