import copy
import datetime
import logging
import pytz
import requests

from dateutil.parser import parse

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from news.models import Source, Article
from news.forms import ArticleModelForm, SourceModelForm

newslogger = logging.getLogger('newslogger')


def save_article_and_source(newapi_article, last_published_at):
    _newapi_article = copy.copy(newapi_article)

    publishedAt = newapi_article.pop("publishedAt",None)
    if publishedAt is None:
        return False

    publishedAt = parse(publishedAt)
    #There are newsapi articles with publishedAt='0001-01-01'
    if publishedAt <= parse(last_published_at):
        log_msg = "New not saved due to date limit."
        log_msg = "%s\n Date limit: %s." %(log_msg, last_published_at)
        log_msg = "%s\n New: %s\n\n" %(log_msg, _newapi_article)
        newslogger.warning(log_msg)
        return False

    newapi_article['publishedAt'] = publishedAt
    source = None
    newapi_source = newapi_article.pop("source")
    newapi_source['newsapi_id'] = newapi_source.pop("id", None) \
                                  or newapi_source["name"]

    source_modelform = SourceModelForm(newapi_source)
    if source_modelform.is_valid():
        source, is_created = Source.objects.get_or_create(
                                    **source_modelform.cleaned_data)
        newapi_article['source'] = "%s" %(source.pk)
    else:
        log_msg = "New not saved due to source validation error."
        log_msg = "%s\n New: %s" % (log_msg, _newapi_article)
        log_msg = "%s\n Validation error: %s\n\n" % (log_msg, source_modelform.errors)
        newslogger.warning(log_msg)
        return False

    article_modelform = ArticleModelForm(newapi_article)
    if article_modelform.is_valid():
        article = article_modelform.save()
        return True
    else:
        log_msg = "New not saved due to new validation error."
        log_msg = "%s\n New: %s" % (log_msg, _newapi_article)
        log_msg = "%s\n Validation error: %s\n\n" % (log_msg, article_modelform.errors)
        newslogger.warning(log_msg)
    return False


class GetArticlesFromNewsAPI(View):
    def get(self, request, *args, **kwargs):
        last_published_at = Article.get_last_published_at()
        new_articles = 0
        loaded_articles = False
        #some english language news media, selected randomly
        sources = ["bbc-news", "reuters", "the-washington-post", "cnn"]

        page = 1
        found_articles = 0
        url = "https://newsapi.org/v2/everything" \
              "?sources=%s" \
              "&from=%s" \
              "&language=en" \
              "&page=%s&apiKey=%s" % (",".join(sources),
                                      last_published_at,
                                      page,
                                      settings.NEWSAPI_KEY)

        while page==1 or found_articles==20:
            page = page + 1
            found_articles = 0

            response = requests.get(url)
            if hasattr(response,"json"):
                json_response = response.json()
                if json_response['status'] == "ok":
                    loaded_articles = True
                    articles = json_response['articles']
                    found_articles = len(articles)

                    for newapi_article in articles:
                        if save_article_and_source(newapi_article, last_published_at):
                            new_articles = new_articles + 1

            url = "https://newsapi.org/v2/everything" \
                  "?sources=%s" \
                  "&from=%s" \
                  "&language=en" \
                  "&page=%s&apiKey=%s" % (",".join(sources),
                                          last_published_at,
                                          page,
                                          settings.NEWSAPI_KEY)

        return JsonResponse({"loaded_articles": loaded_articles,
                            "new_articles": new_articles})


class GetJSONArticles(View):
    num_articles = 100

    def get(self, request, *args, **kwargs):
        articles = Article.objects.order_by("-publishedAt")[:self.num_articles]
        data = []
        for article in articles:
            _data = article.to_dict()
            data.append(_data)
        return JsonResponse(data, safe=False)


class NewsList(ListView):
    model = Article
    template_name = 'news/newslist.html'
    context_object_name = 'news'
    num_articles = 20

    def get_queryset(self, *args, **kwargs):
        qs = super(NewsList, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("-publishedAt")[:self.num_articles]
        return qs