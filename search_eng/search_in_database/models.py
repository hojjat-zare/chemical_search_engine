# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Entities(models.Model):
    entid = models.BigIntegerField(primary_key=True)
    mainname = models.CharField(unique=True, max_length=200)
    enttypeid = models.ForeignKey('Typesofentities', models.CASCADE, db_column='enttypeid')
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entities'

    @staticmethod
    def get_primarykey_fields_name():
        return ['entid']

    def get_primary_key(self):
        return [self.entid]

    def __str__(self):
        return str(self.entid) + '-' + self.mainname + '====>' + self.enttypeid.enttypename


class EntitiesAlternateNames(models.Model):
    eid = models.ForeignKey(Entities, models.CASCADE, db_column='eid')
    drowid = models.BigIntegerField()
    langid = models.ForeignKey('Existinglanguages', models.CASCADE, db_column='langid')
    alternatename = models.CharField(max_length=200)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entities_alternate_names'
        unique_together = (('eid', 'drowid'),)

    @staticmethod
    def get_primarykey_fields_name():
        return ['eid','drowid']

    def get_primary_key(self):
        return [self.eid.entid,self.drowid]

    def __str__(self):
        return eid.mainname + "." + str(self.drowid)+ "=>" + alternatename


class Entitiesrelatedphrases(models.Model):
    entid = models.ForeignKey(Entities, models.CASCADE, db_column='entid')
    phraseid = models.ForeignKey('ExistingPhrases', models.CASCADE, db_column='phraseid')
    comments = models.CharField(max_length=5000, blank=True, null=True)
    drowid = models.BigIntegerField(unique=True, primary_key=True)

    class Meta:
        managed = False
        db_table = 'entitiesrelatedphrases'
        unique_together = (('entid', 'phraseid'),)


    @staticmethod
    def get_primarykey_fields_name():
        return ['entid','phraseid']

    def get_primary_key(self):
        return [self.entid.entid,self.phraseid.phraseid]

    def __str__(self):
        return self.entid.mainname + "=>" + self.phraseid.phrasestring


class EntityRelationEntity(models.Model):
    eid1 = models.ForeignKey(Entities, models.CASCADE, db_column='eid1',related_name='EntityRelationEntity_eid1_set')
    relationid = models.ForeignKey(Entities, models.CASCADE, db_column='relationid',related_name='EntityRelationEntity_relationid_set')
    eid2 = models.ForeignKey(Entities, models.CASCADE, db_column='eid2',related_name='EntityRelationEntity_eid2_set')
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entity_relation_entity'
        unique_together = (('eid1', 'relationid', 'eid2'),)

    @staticmethod
    def get_primarykey_fields_name():
        return ['eid1', 'relationid','eid2']

    def get_primary_key(self):
        return [self.eid1.entid,self.relationid.entid,self.eid2.entid]

    def __str__(self):
        return self.eid1.mainname + "<=(" + self.relationid.mainname + ")=>" + self.eid2.mainname


class EntsBlobPropsValues(models.Model):
    prop_owner_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_owner_eid',related_name='EntsBlobPropsValues_prop_owner_eid_set')
    prop_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_eid',related_name='EntsBlobPropsValues_prop_eid_set')
    drowid = models.IntegerField()
    mimetype = models.CharField(max_length=100, blank=True, null=True)
    dvalue = models.BinaryField(blank=True, null=True)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ents_blob_props_values'
        unique_together = (('prop_owner_eid', 'prop_eid', 'drowid'),)

    @staticmethod
    def get_primarykey_fields_name():
        return ['prop_owner_eid','prop_eid','drowid']

    def get_primary_key(self):
        return [self.prop_owner_eid.entid, self.prop_eid.entid,self.drowid]

    def __str__(self):
        return self.prop_owner_eid.mainname + "." + self.prop_eid.mainname + "[{}]".format(self.drowid) + "=" + mimetype


class EntsDoublePropsValues(models.Model):
    prop_owner_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_owner_eid',related_name='EntsDoublePropsValues_prop_owner_eid_set')
    prop_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_eid',related_name='EntsDoublePropsValues_prop_eid_set')
    drowid = models.IntegerField()
    dvalue = models.FloatField(blank=True, null=True)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ents_double_props_values'
        unique_together = (('prop_owner_eid', 'prop_eid', 'drowid'),)

    @staticmethod
    def get_primarykey_fields_name():
        return ['prop_owner_eid','prop_eid','drowid']

    def get_primary_key(self):
        return [self.prop_owner_eid.entid, self.prop_eid.entid,self.drowid]

    def __str__(self):
        return self.prop_owner_eid.mainname + "." + self.prop_eid.mainname + "[{}]".format(self.drowid) + "=" + str(self.dvalue)


class EntsIntegerPropsValues(models.Model):
    prop_owner_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_owner_eid',related_name='EntsIntegerPropsValues_prop_owner_eid_set')
    prop_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_eid',related_name='EntsIntegerPropsValues_prop_eid_set')
    drowid = models.IntegerField()
    dvalue = models.BigIntegerField(blank=True, null=True)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ents_integer_props_values'
        unique_together = (('prop_owner_eid', 'prop_eid', 'drowid'),)

    @staticmethod
    def get_primarykey_fields_name():
        return ['prop_owner_eid','prop_eid','drowid']

    def get_primary_key(self):
        return [self.prop_owner_eid.entid, self.prop_eid.entid,self.drowid]

    def __str__(self):
        return self.prop_owner_eid.mainname + "." + self.prop_eid.mainname + "[{}]".format(self.drowid) + "=" + str(self.dvalue)


class EntsStringPropsValues(models.Model):
    prop_owner_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_owner_eid',related_name='EntsStringPropsValues_prop_owner_eid_set')
    prop_eid = models.ForeignKey(Entities, models.CASCADE, db_column='prop_eid',related_name='EntsStringPropsValues_prop_eid_set')
    drowid = models.IntegerField()
    langid = models.ForeignKey('Existinglanguages', models.CASCADE, db_column='langid')
    dvalue = models.CharField(max_length=5000, blank=True, null=True)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ents_string_props_values'
        unique_together = (('prop_owner_eid', 'prop_eid', 'drowid', 'langid'),)

    @staticmethod
    def get_primarykey_fields_name():
        return ['prop_owner_eid','prop_eid','drowid','langid']

    def get_primary_key(self):
        return [self.prop_owner_eid.entid, self.prop_eid.entid,self.drowid,self.langid.langid]

    def __str__(self):
        return self.prop_owner_eid.mainname + "." + self.prop_eid.mainname + "[{}]".format(self.drowid) + "=" + self.dvalue


class ExistingPhrases(models.Model):
    phraseid = models.BigIntegerField(primary_key=True)
    phrasestring = models.CharField(unique=True, max_length=200)
    langid = models.ForeignKey('Existinglanguages', models.CASCADE, db_column='langid')
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'existing_phrases'

    @staticmethod
    def get_primarykey_fields_name():
        return ['phraseid']

    def get_primary_key(self):
        return [self.phraseid]

    def __str__(self):
        return str(self.phraseid) + "-" + self.phrasestring


class Existinglanguages(models.Model):
    langid = models.SmallIntegerField(primary_key=True)
    languagenameinenglish = models.CharField(unique=True, max_length=100)
    languagenamebyitself = models.CharField(unique=True, max_length=100)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'existinglanguages'

    @staticmethod
    def get_primarykey_fields_name():
        return ['langid']

    def get_primary_key(self):
        return [self.langid]

    def __str__(self):
        return str(self.langid) + "-" + self.languagenameinenglish


class NewTable(models.Model):
    new_table_fld = models.SmallIntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'new_table'

    @staticmethod
    def get_primarykey_fields_name():
        return ['new_table_fld']

    def get_primary_key(self):
        return [self.new_table_fld]

    def __str__(self):
        return str(self.new_table_fld)


class Typesofentities(models.Model):
    enttypeid = models.SmallIntegerField(primary_key=True)
    enttypename = models.CharField(unique=True, max_length=100)
    comments = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'typesofentities'

    @staticmethod
    def get_primarykey_fields_name():
        return ['enttypeid']

    def get_primary_key(self):
        return [self.enttypeid]

    def __str__(self):
        return str(self.enttypeid) + "-" + self.enttypename


class Searchs(models.Model):
    searchid = models.BigIntegerField(primary_key=True)
    ent_phraseid = models.ForeignKey(Entitiesrelatedphrases, models.DO_NOTHING, db_column='ent_phraseid')
    reference_address = models.CharField(max_length=2000)
    search_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'searchs'

    @staticmethod
    def get_primarykey_fields_name():
        return ['searchid']

    def get_primary_key(self):
        return [self.searchid]

    def __str__(self):
        return str(self.searchid) + "- (" + self.ent_phraseid + ")=>" + self.reference_address + "@(" + self.search_time.strftime("%Y.%m.%d, %H:%M:%S") + ")"


class Results(models.Model):
    resultid = models.BigIntegerField(primary_key=True)
    searchid = models.ForeignKey('Searchs', models.DO_NOTHING, db_column='searchid')
    result = models.BinaryField(blank=True, null=True)
    mimetype = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results'

    @staticmethod
    def get_primarykey_fields_name():
        return ['resultid']

    def get_primary_key(self):
        return [self.resultid]

        ###########  __str__ method is not compeleted (binary field wont be shown) ##########################
    def __str__(self):
        return str(self.resultid) + "- (" + self.searchid.ent_phraseid + "&&" + self.reference_address +")=>"
