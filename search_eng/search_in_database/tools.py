from .models import *
from django.db.models import Q
from django.db import connection

# Entities
id_of_typeOfValue = 1
id_of_unit = 0
id_of_drived_from = 7
id_of_has = 8
id_of_double_with_unit = 3
id_of_entity_property = 4
id_of_double_unitless = 10
id_of_integer_unitless = 11
id_of_string = 12
id_of_blob = 13
id_of_integer_with_unit = 14

# Typesofentities
id_of_property_type = 4
id_of_concept_type = 1
id_of_instance_type = 6



def get_result_for_search(sentence):
    encapsulated_result = []
    sentence_related_entities = SentenceRelatedEntities(sentence)
    proper_results = sentence_related_entities.get_sorted_result_candidates()
    for result_element in proper_results:
        if(result_element.type in ['instance','concept']):
            all_props_of_entity = AllPropertiesOfEntity(result_element.entity).get_all_propes_in_dictionary_form()
            encapsulated_result.append({'entity_name':result_element.entity.mainname,'type':result_element.type,'data':all_props_of_entity})
        else:   # result is property_of_instance
            property_of_entity = PropertyOfEntity(result_element.entity,result_element.property).get_property_value()
            encapsulated_result.append({'entity_name':result_element.entity.mainname,'type':result_element.type,'data':property_of_entity})
    a = encapsulated_result
    # breakpoint()
    return encapsulated_result

def get_result_for_entity(entity_mainname):
    typeid_map_to_name = {id_of_concept_type:'concept',id_of_property_type:'property',id_of_instance_type:'instance'}
    entity = Entities.objects.get(mainname=entity_mainname)
    all_props_of_entity = AllPropertiesOfEntity(entity).get_all_propes_in_dictionary_form()
    return [{'entity_name':entity.mainname, 'type':typeid_map_to_name[entity.enttypeid_id], 'data':all_props_of_entity}]


class AllPropertiesOfEntity:

    def __init__(self,entity):
        self._entity = entity
        entity_id = entity.entid
        self._blob_props = EntsBlobPropsValues.objects.filter(prop_owner_eid=entity_id).select_related('prop_eid').order_by('prop_eid','drowid')
        self._double_props = EntsDoublePropsValues.objects.filter(prop_owner_eid=entity_id).select_related('prop_eid').order_by('prop_eid','drowid')
        self._integer_props = EntsIntegerPropsValues.objects.filter(prop_owner_eid=entity_id).select_related('prop_eid').order_by('prop_eid','drowid')
        self._string_props = EntsStringPropsValues.objects.filter(prop_owner_eid=entity_id).select_related('prop_eid').order_by('prop_eid','drowid')

    def get_propes_in_dictionary_form(self,props_queryset, is_blob = False):
        props = dict()
        for ent_prop in props_queryset:
            if(ent_prop.drowid == 0):
                if(not is_blob):
                    props[ent_prop.prop_eid.mainname] = {'value':[ent_prop.dvalue]}
                else:
                    props[ent_prop.prop_eid.mainname] = {'value':[ent_prop.blob_value(width='auto',height='auto')]}
                    # breakpoint()
            else:
                if(not is_blob == None):
                    props[ent_prop.prop_eid.mainname]['value'].append(ent_prop.dvalue)
                else:
                    props[ent_prop.prop_eid.mainname]['value'].append(ent_prop.blob_value(width='auto',height='auto'))
        return props

    def get_blob_propes_in_dictionary_form(self):
        return self.get_propes_in_dictionary_form(self._blob_props,is_blob=True)

    def get_string_props_in_dictionary_form(self):
        return self.get_propes_in_dictionary_form(self._string_props)

    def get_double_propes_in_dictionary_form(self):
        double_props = dict()
        all_propes = {'double_props':double_props}
        unit_of_property = None
        for ent_prop in self._double_props:
            if(ent_prop.drowid == 0):
                unit_of_property = EntsStringPropsValues.objects.filter(prop_owner_eid=ent_prop.prop_eid,prop_eid=id_of_unit)
                if(len(unit_of_property)==0):
                    double_props[ent_prop.prop_eid.mainname] = {'value':[ent_prop.dvalue],'unit':None}
                else:
                    double_props[ent_prop.prop_eid.mainname] = {'value':[ent_prop.dvalue],'unit':unit_of_property[0].dvalue}
            else:
                double_props[ent_prop.prop_eid.mainname]['value'].append(ent_prop.dvalue)
        return all_propes

    def get_integer_and_entity_propes_in_dictionary_form(self):
        integer_props = dict()
        entity_props = dict()
        all_propes = {'integer_props':integer_props,'entity_props':entity_props}
        unit_of_property = None
        for ent_prop in self._integer_props:
            type_of_prop = EntsIntegerPropsValues.objects.filter(prop_owner_eid = ent_prop.prop_eid , prop_eid = id_of_typeOfValue)
            if(ent_prop.drowid == 0):
                if(len(type_of_prop) == 0):  # means property is integer not id of an entity
                    unit_of_property = EntsStringPropsValues.objects.filter(prop_owner_eid=ent_prop.prop_eid,prop_eid=id_of_unit)
                    if(len(unit_of_property)==0):  # means property has not unit
                        integer_props[ent_prop.prop_eid.mainname] = {'value':[ent_prop.dvalue],'unit':None}
                    else:
                        integer_props[ent_prop.prop_eid.mainname] = {'value':[ent_prop.dvalue],'unit':unit_of_property[0].dvalue}
                else:   # means property is entity
                    if(ent_prop.dvalue != None):
                        equivalent_entity = Entities.objects.get(pk=ent_prop.dvalue)
                        all_props_of_entity = AllPropertiesOfEntity(equivalent_entity).get_all_propes_in_dictionary_form()
                        entity_props[ent_prop.prop_eid.mainname] = {'value':[{'entity_name':equivalent_entity.mainname,'data':all_props_of_entity,'type':"instance"}]}
                    else:
                        entity_props[ent_prop.prop_eid.mainname] = {'value':[]}
            else:
                if(len(type_of_prop) == 0):  # means property is integer not id of an entity
                    unit_of_property = EntsStringPropsValues.objects.filter(prop_owner_eid=ent_prop.prop_eid,prop_eid=id_of_unit)
                    # if(len(unit_of_property)==0):  # means property has not unit
                    #     integer_with_unit_props[ent_prop.prop_eid.mainname]['value'].append(ent_prop.dvalue)
                    # else:
                    integer_props[ent_prop.prop_eid.mainname]['value'].append(ent_prop.dvalue)
                else:  # means property is entity
                    if(ent_prop.dvalue != None):
                        equivalent_entity = Entities.objects.get(pk=ent_prop.dvalue)
                        all_props_of_entity = AllPropertiesOfEntity(equivalent_entity).get_all_propes_in_dictionary_form()
                        entity_props[ent_prop.prop_eid.mainname]['value'].append({'entity_name':equivalent_entity.mainname,'data':all_props_of_entity,'type':"instance"})
                    else:
                        entity_props[ent_prop.prop_eid.mainname]['value'].append(None)
        return all_propes


    def get_all_propes_in_dictionary_form(self):
        props = {'numeric':dict(),'string':dict(),'entity':dict(),'blob':dict()}
        props['blob'] = self.get_blob_propes_in_dictionary_form()
        double_props = self.get_double_propes_in_dictionary_form()
        props['numeric'].update(double_props['double_props'])
        props['string'] = self.get_string_props_in_dictionary_form()
        integer_and_entity_props = self.get_integer_and_entity_propes_in_dictionary_form()
        props['numeric'].update(integer_and_entity_props['integer_props'])
        props['entity'] = integer_and_entity_props['entity_props']
        return props


class PropertyOfEntity:
    def __init__(self,entity, property):
        self._entity = entity
        self._property = property

    def get_entity_id(self):
        return self._entity.entid

    def get_property_mainname(self):
        return self._property.mainname

    def get_property_id(self):
        return self._property.entid

    def get_table_name_of_property(self):
        type_of_prop_id = EntityRelationEntity.objects.get(eid1 = self._property.entid, relationid = id_of_drived_from).eid2_id
        if(type_of_prop_id in [id_of_double_unitless ,  id_of_double_with_unit]):
            return 'entsdoublepropsvalues'
        elif(type_of_prop_id == id_of_blob):
            return 'entsblobpropsvalues'
        elif(type_of_prop_id == id_of_string):
            return 'entsstringpropsvalues'
        elif(type_of_prop_id in [id_of_entity_property, id_of_integer_unitless, id_of_integer_with_unit]):
            return 'entsintegerpropsvalues'

    def get_property_value(self):
        type_of_prop_id = EntityRelationEntity.objects.get(eid1 = self._property.entid, relationid = id_of_drived_from).eid2_id
        properties = None
        prop_type_map = {id_of_double_with_unit:'numeric', id_of_integer_with_unit:'numeric',id_of_double_unitless:'numeric',id_of_integer_unitless:'numeric',id_of_string:'string',id_of_blob:'blob',id_of_entity_property:'entity'}
        if(type_of_prop_id in [id_of_double_unitless ,  id_of_double_with_unit]): # property is an double
            properties = EntsDoublePropsValues.objects.filter(prop_owner_eid=self.get_entity_id(), prop_eid=self.get_property_id()).order_by('drowid')
        elif(type_of_prop_id == id_of_blob):
            properties = EntsBlobPropsValues.objects.filter(prop_owner_eid=self.get_entity_id(), prop_eid=self.get_property_id()).order_by('drowid')
        elif(type_of_prop_id == id_of_string):
            properties = EntsStringPropsValues.objects.filter(prop_owner_eid=self.get_entity_id(), prop_eid=self.get_property_id()).order_by('drowid')
        elif(type_of_prop_id in [id_of_entity_property, id_of_integer_unitless, id_of_integer_with_unit]): # property is an integer
            properties = EntsIntegerPropsValues.objects.filter(prop_owner_eid=self.get_entity_id(), prop_eid=self.get_property_id()).order_by('drowid')
        if(type_of_prop_id in [id_of_double_with_unit, id_of_integer_with_unit]):
            unit_of_property = EntsStringPropsValues.objects.get(prop_owner_eid=self.get_property_id(), prop_eid=id_of_unit)
            return{prop_type_map[type_of_prop_id]:{self.get_property_mainname():{'value':[prop.dvalue for prop in properties],'unit':unit_of_property.dvalue}}}
        elif(type_of_prop_id in [id_of_double_unitless,id_of_integer_unitless,id_of_string]):
            return{prop_type_map[type_of_prop_id]:{self.get_property_mainname():{'value':[prop.dvalue for prop in properties]}}}
        elif(type_of_prop_id == id_of_blob):
            return{prop_type_map[type_of_prop_id]:{self.get_property_mainname():{'value':[prop.blob_value(width='auto',height='auto') for prop in properties]}}}
        elif(type_of_prop_id == id_of_entity_property):
            value = []
            for prop in properties:
                if(prop.dvalue!= None):
                    equivalent_entity = Entities.objects.get(pk=prop.dvalue)
                    all_props_of_entity = AllPropertiesOfEntity(equivalent_entity).get_all_propes_in_dictionary_form()
                    value.append(all_props_of_entity)
                else:
                    value.append({'entity_name':None,'data':None,'type':'instance'})
            return{prop_type_map[type_of_prop_id]:{self.get_property_mainname():{'value':value}}}



class ObjectRelatedString:
    def __init__(self, object):
        self._object = object
        self._entities = None
        self._alternate_names = None
        self._related_phrases = None
        self._properties = None
        self._find_entities()
        self._find_alternate_names()
        self._find_related_phrases()
        self._find_properties()


    def _find_entities(self):
        pass

    def _find_alternate_names(self):
        entities_id = self._entities.values_list('entid',flat=True)
        self._alternate_names = EntitiesAlternateNames.objects.filter(eid__in = list(entities_id))


    def _find_related_phrases(self):
        entities_id = self._entities.values_list('entid',flat=True)
        self._related_phrases = Entitiesrelatedphrases.objects.select_related('phraseid','entid').filter(entid__in = list(entities_id))

    def _find_properties(self):
        entities_id = self._entities.values_list('entid',flat=True)
        self._properties = EntityRelationEntity.objects.select_related('eid','relationid','eid2').filter(Q(eid1__in = list(entities_id)) , Q(relationid = id_of_has))

    def does_exist_entity(self):
        if(len(self._entities) == 0):
            return False
        return True

    def get_word(self):
        return self._object

    def get_entities(self):
        return self._entities

    # instance firest then concepts then properties
    def get_entities_sorted(self):
        def manual_sort(entity):
            if(entity.enttypeid_id==id_of_instance_type):
                return 1
            if(entity.enttypeid_id==id_of_concept_type):
                return 2
            if(entity.enttypeid_id==id_of_property_type):
                return 3
        sorted_list = list(self._entities)
        sorted_list.sort(key=manual_sort)
        return sorted_list

    # remember to test this method
    def get_related_entities_mainname(self):
        return list(self._entities.values_list('mainname',flat=True))

    # remember to test thism method
    def get_alternatenames(self):
        list_form = list(self._alternate_names.values_list('eid__mainname','alternatename'))
        # dict_form = dict()
        # for ent in self.get_related_entities_mainname():
        #     dict_form[ent] = []
        # for ent_altname in list_form:
        #     dict_form[ent_altname[0]] = ent_altname[1]
        return list_form

    def get_related_phrasestrings(self):
        return list(self._related_phrases.values_list('entid__mainname','phraseid__phrasestring'))

    def get_properties_mainname(self):
        return list(self._properties.values_list('eid1__mainname','eid2__mainname'))

    def get_properties_id(self):
        return list(self._properties.distinct().values_list('eid2__entid',flat=True))


class WordRelatedStrings(ObjectRelatedString):
    def __init__(self,word):
        super().__init__(word)

    def _find_entities(self):
        word = self._object
        query_to_ents_alter_names = EntitiesAlternateNames.objects.filter(alternatename__contains = word).values('eid')
        query_to_ents_rel_phr = Entitiesrelatedphrases.objects.filter(phraseid__phrasestring__contains=word).values('entid')
        query_to_get_entities = Entities.objects.filter(Q(enttypeid__in = [id_of_concept_type,id_of_property_type,id_of_instance_type]) & (Q(mainname__contains = word) | Q(entid__in =query_to_ents_rel_phr) | Q(entid__in=query_to_ents_alter_names)) )
        self._entities = query_to_get_entities

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
        return list(self._properties.distinct().values_list('eid2__mainname',flat=True))



class EntityRelatedStrings(ObjectRelatedString):
    def __init__(self,entity_pk):
        super().__init__(entity_pk)


    def _find_entities(self):
        pk = self._object
        query_to_get_entities = Entities.objects.filter(pk = pk)
        self._entities = query_to_get_entities


class SentenceRelatedEntities:
    prepositions = ['to', 'of', 'by', 'on', 'for', 'at', 'from', 'in','how','what']
    def __init__(self,sentence):
        self._sentence = sentence
        self._identified_sentence = self._identify_sentence()
        self._wordsRelatedStrings = []
        self._entities = []
        for i in range(len(self._identified_sentence)):
            if(not self._identified_sentence[i]['is_preposition']):
                wrs = WordRelatedStrings(self._identified_sentence[i]['word'])
                self._wordsRelatedStrings.append({'word_related_string':wrs,'place':i})
                self._entities.append({'entities':wrs.get_entities_sorted(),'place':i})

    def _identify_sentence(self):
        words = self._sentence.split(' ')
        identified_sentence = []
        for word in words:
            is_preposition = False
            if(word in SentenceRelatedEntities.prepositions):
                is_preposition = True
            identified_sentence.append({'word':word,'is_preposition':is_preposition})
        return identified_sentence

    def get_words_except_prepositions(self):
        words = []
        count = 0
        for element in self._identified_sentence:
            if(not element['is_preposition']):
                words.append({'word':element['word'],'place':count})
            count += 1
        return words

    # def get_compound_words(self):
    #     compound_words = []
    #     sentence_element = self.get_words_except_prepositions()
    #     previous_word = None
    #     for element in sentence_element:
    #         if(previous_word !=None):
    #             compound = '{} {}'.format(previous_word['word'],element['word'])
    #             compound_WordRelatedString = WordRelatedStrings(compound)
    #             if(compound_WordRelatedString.does_exist_entity()):
    #                 compound_words.append({'compound_word':compound,'entities':compound_WordRelatedString.get_entities(),'first_place':previous_word['place'],'second_place':element['place']})
    #         previous_word = element
    #     return compound_words


    def get_pairs_of_property_instance(self):
        pairs = []
        previous_element = None
        for element in self.get_entities():
            if(previous_element != None):
                for ent in previous_element['entities']:
                    for second_ent in element['entities']:
                        if(ent.entid in EntityRelatedStrings(second_ent.entid).get_properties_id()):
                            pairs.append({'property':ent,'instance':second_ent,'property_place':previous_element['place'],'instance_place':element['place']})
                        elif(second_ent.entid in EntityRelatedStrings(ent.entid).get_properties_id()):
                            pairs.append({'property':second_ent,'instance':ent,'instance_place':previous_element['place'],'property_place':element['place']})
            previous_element = element
        return pairs

    def get_sorted_result_candidates(self):
        seperate_entities = self.get_entities()
        pairs_of_property_instance = self.get_pairs_of_property_instance()
        # compound_words = self.get_compound_words()
        concept_search_special_words = {'what ':'','how to ':''}
        property_search_special_words = {'how much ':'',' of ':' of '}
        is_search_about_concept = False
        is_search_about_property = False
        modified_sentence = self.get_sentence()
        for word in concept_search_special_words:
            if(word in self.get_sentence()):
                is_search_about_concept = True
                modified_sentence = self.get_sentence().replace(word,concept_search_special_words[word])
        for word in property_search_special_words:
            if(word in self.get_sentence()):
                is_search_about_property = True
                modified_sentence = self.get_sentence().replace(word,property_search_special_words[word])
        results = self.get_primary_result(modified_sentence,pairs_of_property_instance)
        if(is_search_about_concept):
            results.increase_concepts_rate(30)
        elif(is_search_about_property):
            results.increase_propertyOfInstances_rate(20)
        return results.get_all_results_sorted()


    def get_primary_result(self,modified_sentence,pairs_of_property_instance):
        result_candidates = ResultCandidates()
        query_for_whole_sentence = WordRelatedStrings(modified_sentence)
        typeid_map_to_name = {id_of_concept_type:'concept',id_of_property_type:'property',id_of_instance_type:'instance'}
        for pair in self.get_pairs_of_property_instance():
            result_candidates.add_result('property_of_instance',pair['instance'],10,pair['property'])
        if(query_for_whole_sentence.does_exist_entity()):
            for ent in query_for_whole_sentence.get_entities_sorted():
                result_candidates.add_result(typeid_map_to_name[ent.enttypeid_id],ent,100)
                # return result_candidates
        # breakpoint()
        for quertyset in self.get_entities():
            for entity in quertyset['entities']:
                # breakpoint()
                result_candidates.add_result(typeid_map_to_name[entity.enttypeid_id],entity,10)
        return result_candidates

    def get_correspond_pair_of_prop_instances(self,entity,pairs_of_property_instance):
        pairs = []
        for pair in pairs_of_property_instance:
            if(entity == pair['instance'] or entity == pair['property']):
                pairs.append(pair)
        return pairs

    def get_sentence(self):
        return self._sentence

    def get_identified_sentence(self):
        return self._identified_sentence

    def get_wordsRelatedStrings(self):
        return self._wordsRelatedStrings

    def get_entities(self):
        return self._entities


class ResultCandidates:
    def __init__(self):
        self._results = []

    def add_result(self,type,entity,rate,property=None):
        # entitt_enttypeid_map = {'instance':6,'concept':1,'property':4}
        if(entity.enttypeid_id != id_of_property_type):
            result_element = ResultElement(type,entity,rate, property)
            operation_has_done = self.increase_rate_of(result_element,rate)
            if(not operation_has_done):
                self.get_all_results().append(result_element)
        else:
            for result in self.get_all_results():
                if(result.property == entity):
                    result.increase_rate(rate)

    def increase_rate_of(self,result_element,amount):
        is_there_item = False
        for result in self.get_all_results():
            if(result.are_entities_equal(result_element) and (result_element.property==None)):
                result.increase_rate(amount)
                is_there_item = True
        return is_there_item

    def _increase_type_rate(self,type,amount):
        for result in self.get_all_results():
            if(result.type == type):
                result.increase_rate(amount)

    def increase_concepts_rate(self,amount):
        self._increase_type_rate('concept',amount)

    def increase_propertyOfInstances_rate(self,amount):
        self._increase_type_rate('property_of_instance',amount)

    def sort_by_rate(self):
        self._results.sort(key=lambda result: result.rate,reverse=True)

    def get_all_results(self):
        return self._results

    def get_all_results_sorted(self):
        self.sort_by_rate()
        return self._results

    def __str__(self):
        answer = '<ResultCandidates ['
        for result in self.get_all_results():
            answer = answer + str(result)+'\n '
        answer = answer + '] >'
        return answer
    def __repr__(self):
        return str(self)


class ResultElement:
    def __init__(self,type,entity,rate,property=None):
        type_allowed_inputs = ['instance','concept','property_of_instance']
        if(not type in type_allowed_inputs):
            raise ValueError('invalid input, type must be one of {}'.format(type_allowed_inputs))
        self.type = type
        self.entity = entity
        self.property = property
        self.rate = rate

    def __eq__(self,obj):
        return(self.type==obj.type and self.entity == obj.entity and self.property== obj.property)

    def are_entities_equal(self,obj):
        return(self.entity == obj.entity)

    def are_properties_equal(self,obj):
        return self.property == obj.property

    def increase_rate(self,amount):
        self.rate = self.rate + amount

    def __str__(self):
        return '<type:{},entity:{},property:{},rate:{}>'.format(self.type,str(self.entity),str(self.property),self.rate)

    def __repr__(self):
        return str(self)
