from .models import *
from django.db.models import Q


class ObjectRelatedString:
    def __init__(self,object):
        self._object = object
        self._entities = self._find_and_get_entities()
        self._alternate_names = []
        self._has_alternate_names_searched = False
        self._related_phrases = []
        self._has_related_phrases_searched = False
        self._properties = []
        self._has_properties_searched = False

    def _find_and_get_entities():
        pass

    def get_word(self):
        return self._object

    def get_entities(self):
        return self._entities

    # remember to test this method
    def get_related_entities_mainname(self):
        return list(self._entities.values_list('mainname',flat=True))


    def _find_alternate_names(self):
        if(not self._has_alternate_names_searched):
            entities_id = self._entities.values_list('entid',flat=True)
            self._alternate_names = EntitiesAlternateNames.objects.filter(eid__in = list(entities_id))

    # remember to test thism method
    def get_alternatenames(self):
        self._find_alternate_names()
        list_form = list(self._alternate_names.values_list('eid__mainname','alternatename'))
        # dict_form = dict()
        # for ent in self.get_related_entities_mainname():
        #     dict_form[ent] = []
        # for ent_altname in list_form:
        #     dict_form[ent_altname[0]] = ent_altname[1]
        return list_form


    def _find_related_phrases(self):
        if(not self._has_related_phrases_searched):
            entities_id = self._entities.values_list('entid',flat=True)
            self._related_phrases = Entitiesrelatedphrases.objects.select_related('phraseid','entid').filter(entid__in = list(entities_id))

    def get_related_phrasestrings(self):
        self._find_related_phrases()
        return list(self._related_phrases.values_list('entid__mainname','phraseid__phrasestring'))

    def _find_properties(self):
        if(not self._has_properties_searched):
            entities_id = self._entities.values_list('entid',flat=True)
            self._properties = EntityRelationEntity.objects.select_related('eid','relationid','eid2').filter(Q(eid1__in = list(entities_id)) , Q(relationid = 8))
             # 8 is id of 'has'

    def get_properties_mainname(self):
        self._find_properties()
        return list(self._properties.values_list('eid1__mainname','eid2__mainname'))






class WordRelatedStrings(ObjectRelatedString):
    def __init__(self,word):
        super().__init__(word)

    def _find_and_get_entities(self):
        word = self._object
        query_to_ents_alter_names = EntitiesAlternateNames.objects.filter(alternatename__contains = word).values('eid')
        query_to_ents_rel_phr = Entitiesrelatedphrases.objects.filter(phraseid__phrasestring__contains=word).values('entid')
        query_to_get_entities = Entities.objects.filter(Q(mainname__contains = word) | Q(entid__in =query_to_ents_rel_phr) | Q(entid__in=query_to_ents_alter_names) )
        return query_to_get_entities

    def get_related_words_for_scrapy_site_evaluation(self):
        self._find_alternate_names()
        self._find_related_phrases()
        words = self.get_related_entities_mainname()
        for word in self.get_alternatenames():
            words.append(word[1])
        for word in self.get_related_phrasestrings():
            words.append(word[1])
        return words

    def get_properties_for_site_scraping(self):
        self._find_properties()
        return list(self._properties.distinct().values_list('eid2__mainname',flat=True))



class EntitiyRelatedStrings(ObjectRelatedString):
    def __init__(self,entity_pk):
        super().__init__(entity_pk)


    def _find_and_get_entities(self):
        pk = self._object
        query_to_get_entities = Entities.objects.filter(pk = pk)
        return query_to_get_entities

# class StringRelatedStrings:
#     def __init__(self,string):
#         self._string = string
#         self._objects = string.split(' ')
#         self._objectsRelatedStrings = []
#         self._related_entites = []
#         self._objects_for_rating = []
#         self._objects_for_scraping = []
#
#     def get_related_entities():
#         for word in self._objects:
#             wrs = WordRelatedStrings(word)
#             self._objectsRelatedStrings.append(wrs)
#             self._related_entites.append(tuple([word,wrs.get_related_entities()]))
#             self._objects_for_rating.append(tuple([]))
#         self._objects_for_rating.append(tuple([]))
#         for wrs in self._objectsRelatedStrings:
#             self._related_entites.append(tuple([wrs.get_]))
