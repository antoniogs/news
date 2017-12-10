import datetime
import pytz
import uuid

from django.conf import settings
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False)
    source = models.ForeignKey("source", blank=True, null= True,
                               default= None, )
    author = models.CharField(_("author"), max_length=255,
                              blank=True, null= True, default= None )
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))
    url = models.CharField(_("url"), max_length=255)
    urlToImage = models.CharField(_("url to the image"),
                                  max_length=255, blank=True, null= True,
                                  default= None )
    publishedAt = models.DateTimeField( _("published at"))


    def to_dict(self):
        dict = model_to_dict(
                    self,
                    fields = ["id",
                        "author",
                        "title",
                        "description",
                        "url",
                        "urlToImage",
                        "publishedAt",
                    ],
                )
        if self.source is not None:
            dict["source"] = self.source.to_dict()
        else:
            dict["source"] = None

        return dict


    def __str__(self):
        return self.title or ""


    """
    Get the newest publishedAt
    or, if there is not records, 60 minutes before the current time.
    Return an string.
    """
    @classmethod
    def get_last_published_at(self):
        last_article = self.objects.exclude(publishedAt__isnull=True).\
                                        order_by('-publishedAt').first()
        if last_article is not None:
            last_published_at = last_article.publishedAt
        else:
            last_published_at = datetime.datetime.now() \
                                - datetime.timedelta(minutes=60)

        if last_published_at.tzinfo is None:
            #Lets set the tzinfo to the local timezone
            local_tz = pytz.timezone(settings.TIME_ZONE)
            last_published_at = local_tz.localize(last_published_at)

        # Lets modify the date for use UTC timezone
        last_published_at = last_published_at.astimezone(pytz.utc)
        last_published_at = last_published_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        return last_published_at


    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        ordering = ["-publishedAt",]


class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False)
    newsapi_id = models.CharField(_("newsapi id"), max_length=255,
                                  blank=True, null= True, default= None )
    name = models.CharField(_("name"), max_length=255, blank=True,
                            null=True, default=None)


    def __str__(self):
        return self.name or ""


    def to_dict(self):
        dict = model_to_dict(
                    self,
                    fields = ["id",
                        "newsapi_id",
                        "name",
                    ],
                )

        return dict


    class Meta:
        verbose_name = _("source")
        verbose_name_plural = _("sources")
        ordering = ["name",]