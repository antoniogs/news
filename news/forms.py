import bleach
import re
from urllib.parse import urlparse
from urllib.request import urlopen

from django import forms

from news.models import Article, Source


"""
get_valid_url_or_none check if the url exists.
Return None if a valid response is not received from the url,
or the url(string) if there is an valid response
"""
def get_valid_url_or_none(url):
    if url.startswith("http://") or url.startswith("https://"):
        try:
            response = urlopen(url)
            if response.code == 200:
                return url
            return None
        except:
            #Any kind of error means that this is not a valid and active url
            return None

    if url.startswith("//"):
        _url = "http:%s" % (_url)
        try:
            response = urlopen(_url)
            if response.code == 200:
                return _url
        except:
            _url = "https:%s" % (_url)
            try:
                response = urlopen(_url)
                if response.code == 200:
                    return _url
            except:
                return None

    return None


"""
Function that replace some javascript special chars by an html char.
Many chars can be replaced by a html equivalent, as the new-line char,
but others, as explain the https://www.w3schools.com/js/js_strings.asp page,
dont have a html sense.
"""
def js_to_html_replacements(string):
    _string = string
    _string = re.sub("\\r\\n", "<br />", _string)
    _string = re.sub("\\r", "<br />", _string)
    _string = re.sub("\\n", "<br />", _string)
    return _string


class ArticleModelForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'


    # @property
    # def errors(self):
    #     if self._errors is None:
    #         self.full_clean()
    #     return self._errors
    # Django is not checking the form errors
    # because self._errors is always an empty dict, not None.
    # So, let's override the errors method
    @property
    def errors(self):
        self.full_clean()
        return self._errors


    def clean_author(self):
        author = self.cleaned_data.get('author', None)
        if author is None:
            return None
        return js_to_html_replacements(bleach.clean(author))


    def clean_title(self):
        title = self.cleaned_data.get('title', None)
        if title is None:
            return None
        return js_to_html_replacements(bleach.clean(title))


    def clean_description(self):
        description = self.cleaned_data.get('description', None)
        if description is None:
            return None
        description = bleach.clean(description, tags=['br','i', 'mark',
                                                      'p', 'q', 'small',
                                                      'strong', 'sub',
                                                      'sup', 'u', 'wbr'
                                                    ]
                                   )
        return js_to_html_replacements(description)


    def clean_urlToImage(self):
        urlToImage = self.cleaned_data.get('urlToImage',None)
        if urlToImage is None:
            return None

        if urlToImage.startswith("/"):
            #Maybe image path relative to the article domain
            url = self.cleaned_data.get('url', None)
            if url is not None:
                parsed_data = urlparse(url)
                urlToImage = "%s://%s%s" %(parsed_data.scheme,
                                           parsed_data.hostname,
                                           urlToImage)

        urlToImage = get_valid_url_or_none(urlToImage)
        if urlToImage is not None:
            return urlToImage
        return None


    def clean_url(self):
        url = self.cleaned_data.get('url', None)
        if url is None:
            return None

        url = get_valid_url_or_none(url)
        if url is not None:
            return url
        return None


class SourceModelForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = '__all__'


    @property
    def errors(self):
        self.full_clean()
        return self._errors


    def clean_name(self):
        name = self.cleaned_data.get('name', None)
        if name is None:
            return None
        return js_to_html_replacements(bleach.clean(name))


    def clean_newsapi_id(self):
        newsapi_id = self.cleaned_data.get('newsapi_id', None)
        if newsapi_id is None:
            return None
        return bleach.clean(newsapi_id)