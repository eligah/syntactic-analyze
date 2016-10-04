# coding:utf-8
import csv

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views import generic

from batching.models import Keyword
from batching.weibo.scrawl import crawl


def batching(request):
    return render(request, 'batching/demo.html')


def analysis(request):
    # get the keyword
    try:
        keyword = request.POST['input']
    except KeyError:
        return render(request, 'batching/demo.html')

    print "Analysis Keyword: %s" % keyword

    m_keyword, created = Keyword.objects.get_or_create(keyword_text=keyword)
    m_keyword.request_count += 1
    m_keyword.request_date = timezone.now()
    m_keyword.save()

    # if m_keyword.cloud_csv is None:
    crawl(m_keyword.keyword_text, m_keyword.id)

    return HttpResponseRedirect(reverse('batching:result', args=(m_keyword.id,)))


class ResultView(generic.DetailView):
    model = Keyword
    template_name = 'batching/result.html'

    def get_context_data(self, **kwargs):
        context = super(ResultView, self).get_context_data(**kwargs)
        with open('dataFolder/radar_data.csv', 'rb') as csv_file:
            reader = csv.reader(csv_file)
            c = []
            for row in reader:
                c.append(row)
            context['radar_data'] = c

        with open('dataFolder/cloud_features.csv', 'rb') as cloud:
            reader = csv.reader(cloud)
            c = []
            for row in reader:
                c.append(row)
            context['cloud_data'] = c
        return context
