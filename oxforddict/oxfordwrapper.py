#!/bin/env python3.5
import json
import http.client

from .exceptions import *


class OxfordDictionary(object):
    """Simple wrapper for Oxford Dictionary API
    Address: https://www.oxforddictionaries.com/
    API reference: https://developer.oxforddictionaries.com/documentation

    """

    __slots__ = ('app_key', 'app_id', 'lang', '_httpsconn', '_base_url')

    def __init__(self, app_key, app_id, lang='en'):
        """Create OxfordDictionaty object"""
        self.app_key = app_key
        self.app_id = app_id
        self.setlang(lang)
        self._httpsconn = http.client.HTTPSConnection(
            "od-api.oxforddictionaries.com")

    def __repr__(self):
        return "<OxfordDictionary(lang={})>".format(self.lang)

    def __str__(self):
        return self.__repr__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_code, exc_tb):
        self._httpsconn.close()
        if exc_type is None:
            return
        return False

    def setlang(self, lang):
        # Check for supported languages
        if lang.lower() not in ('en', 'es', 'ms', 'sw', 'tn', 'nso',
                                'lv', 'id', 'ur', 'zu', 'ro', 'hi'):
            raise UnsupportedLanguageException(0, "Current language "
                                               "is not supported")

        self.lang = lang
        self._base_url = 'https://od-api.oxforddictionaries.com:443/api/v1'
        # URL/{category}/{source_lang}/{word}/{options}

    def _parseword(self, word):
        # Convert unicode cahracters to HTTP form (%c3%b1)
        word = ''.join(map(lambda x: ''.join('%{:x}'.format(i)
            for i in x.encode('utf-8')) if x > 'z' else x, word))
        # Convert word to required form
        return word.strip().lower().replace(' ', '_')

    def _request(self, *args,  category='', arguments='', set_lang=None):
        if set_lang is None:
            set_lang = self.lang

        self._httpsconn.request('GET', '/'.join([self._base_url,
                                category, set_lang, *args]) + arguments,
                                headers={"app_id": self.app_id,
                                "app_key": self.app_key})
        r = self._httpsconn.getresponse()
        # https://developer.oxforddictionaries.com/documentation/response-codes
        if r.status != 200:
            if r.status == 403:
                raise AuthenticationError(r.status, "The request failed due "
                    "to invalid credentials.")
            elif r.status == 404:
                raise WordNotFoundException(r.status, "No information "
                    "available or the requested URL was not found "
                    "on the server.")
            elif r.status == 400:
                raise BadRequestException(r.status, "The request was invalid "
                    "or cannot be otherwise served. An accompanying error "
                    "message will explain further.")
            elif 500 <= r.status <= 504:
                raise ServiceUnavailableError(r.status, "Error on server side")

        return json.loads(r.read().decode('utf-8'))

    def entries(self, word, *args):
        """Retrieve available dictionary entries for a given word and
        language.
        args can be:
        - regions={region}
        - {filters}
        - definitions
        - examples
        - pronunciations

        For example:
        d.entries('cat', 'examples')

        """

        return self._request(self._parseword(word), *args, category='entries')

    def lemmatron(self, word, *filters):
        """Retrieve available lemmas for a given inflected wordform.
        :word: string with the word
        :*filters: (optional) filter results by categories. Separate
        filtering conditions using a semicolon. Conditions take values
        grammaticalFeatures and/or lexicalCategory and are
        case-sensitive. To list multiple values in single condition
        divide them with comma.

        """

        return self._request(self._parseword(word), *filters,
                             category='inflections')

    def translation(self, word, target_lang):
        """Translate the word to target_lang
        :word: string with the word
        :target_lang: target language
        In case of unsupported target language WordNotFoundException
        will be thrown

        """
        return self._request(self._parseword(word), 'translations=%s' %
                             target_lang, category='entries')

    def wordlist(self, *filters, **advanced_params):
        """Retrieve list of words for particular domain, lexical
        category register and/or region.
        :*filters: Semicolon separated list of wordlist parameters,
        presented as value pairs:

        :limit: Limit the number of results per response. Default and
        maximum limit is 5000.
        :offset: Offset the start number of the result.
        Advanced params:
        :exclude: Semicolon separated list of parameters-value pairs
        (same as filters).
        :exclude_senses: Semicolon separated list of parameters-value
        pairs (same as filters).
        :exclude_prime_sentences: Semicolon separated list of
        parameters-value pairs (same as filters).
        :word_length: Parameter to speficy the minimum (>), exact or
        maximum (<) length
        of the words required.
        :prefix: Filter words that start with prefix parameter
        :exa1ct: If exact=true wordlist returns a list of entries that
        exactly matches the search string.

        LexicalCategory, domains, regions, registers.
        Example for basic filters:
            "registers=Rare;domains=Art"
        Example for advanced filters:
            "lexicalCategory=Noun;domains=sport"

        """
        return self._request(*filters, category='wordlist',
            arguments="?" + "&".join(["%s=%s" % (k, v)
                                      for k, v in advanced_params.items()]))

    def thesaurus(self, word, antonyms=False, synonyms=False):
        if antonyms:
            op = "antonyms"
        elif synonyms:
            op = "synonyms"
        else:
            op = "antonyms;synonyms"

        return self._request(self._parseword(word), op, category='entries')

    def search(self, query, prefix=False, regions=None,
               limit=5000, offset=None):
        """Retrieve available results for a search query and language.
        :query: Search string.
        :prefix: Set prefix to true if you'd like to get results only
        starting with search string.
        :regions: Filter words with specific region(s) E.g., regions=us.
        :limit: Limit the number of results per response. Default and
        maximum limit is 5000.
        :offset: Offset the start number of the result.

        """
        arguments = "?q=%s" % self._parseword(query)
        arguments += "&prefix=%s" % bool(prefix).lower() if prefix else ""
        arguments += "&regions=%s" % regions if regions else ""
        arguments += "&limit=%s" % limit if limit else ""
        arguments += "&offset=%s" % offset if offset else ""

        return self._request(category='search', arguments=arguments)

    def sentences(self, word):
        """Retrieve list of sentences and list of senses (English
        language only).
        :word: An Entry identifier. Case-sensitive.

        """
        return self._request(self._parseword(word), 'sentences',
                             category='entries')

    def utility_languages(self):
        return self._request(category='languages', set_lang='')
        #pass

    def utility_filters(self, entpoint=''):
        # return self._request(category='filters', )
        pass

    def utility_lexicalcategories(self, language):
        pass

    def utility_registers(self, source_lang, target_lang=''):
        pass

    def utility_domains(self, source_lang, target_lang=''):
        pass

    def utility_regions(self, source_lang):
        pass

    def utility_grammatiocalFeatures(self, source_lang):
        pass
