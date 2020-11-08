SELECT  "ENTITIESRELATEDPHRASES"."ENTID",
 "ENTITIESRELATEDPHRASES"."PHRASEID", "ENTITIESRELATEDPHRASES"."COMMENTS",
 "ENTITIESRELATEDPHRASES"."DROWID", "ENTITIES"."ENTID",
 "ENTITIES"."MAINNAME", "ENTITIES"."ENTTYPEID", "ENTITIES"."COMMENTS" FROM
 "ENTITIESRELATEDPHRASES" INNER JOIN "EXISTING_PHRASES" ON
 ("ENTITIESRELATEDPHRASES"."PHRASEID" = "EXISTING_PHRASES"."PHRASEID") INNER
 JOIN "ENTITIES" ON ("ENTITIESRELATEDPHRASES"."ENTID" = "ENTITIES"."ENTID")
 WHERE "EXISTING_PHRASES"."PHRASESTRING" LIKE %roge% ESCAPE\\\\


SELECT  "ENTITIESRELATEDPHRASES"."ENTID",
 "ENTITIESRELATEDPHRASES"."PHRASEID", "ENTITIESRELATEDPHRASES"."COMMENTS",
 "ENTITIESRELATEDPHRASES"."DROWID", "ENTITIES"."ENTID",
 "ENTITIES"."MAINNAME", "ENTITIES"."ENTTYPEID", "ENTITIES"."COMMENTS" FROM
 "ENTITIESRELATEDPHRASES" INNER JOIN "EXISTING_PHRASES" ON
 ("ENTITIESRELATEDPHRASES"."PHRASEID" = "EXISTING_PHRASES"."PHRASEID") INNER
 JOIN "ENTITIES" ON ("ENTITIESRELATEDPHRASES"."ENTID" = "ENTITIES"."ENTID")
 WHERE "EXISTING_PHRASES"."PHRASESTRING" LIKE %roge% ESCAPE\\\\


(SELECT  "ENTITIES"."ENTID", "ENTITIES"."MAINNAME", "ENTITIES"."ENTTYPEID",
 "ENTITIES"."COMMENTS" FROM "ENTITIES" WHERE "ENTITIES"."ENTID" IN (SELECT
 U0."ENTID" AS Col1 FROM "ENTITIESRELATEDPHRASES" U0 INNER JOIN
 "EXISTING_PHRASES" U1 ON (U0."PHRASEID" = U1."PHRASEID") WHERE
 U1."PHRASESTRING" LIKE %roge% ESCAPE\\\\))

(SELECT  "ENTITIESRELATEDPHRASES"."ENTID",
 "ENTITIESRELATEDPHRASES"."PHRASEID", "ENTITIESRELATEDPHRASES"."COMMENTS",
 "ENTITIESRELATEDPHRASES"."DROWID", "ENTITIES"."ENTID",
 "ENTITIES"."MAINNAME", "ENTITIES"."ENTTYPEID", "ENTITIES"."COMMENTS",
 "EXISTING_PHRASES"."PHRASEID", "EXISTING_PHRASES"."PHRASESTRING",
 "EXISTING_PHRASES"."LANGID", "EXISTING_PHRASES"."COMMENTS" FROM
 "ENTITIESRELATEDPHRASES" INNER JOIN "ENTITIES" ON
 ("ENTITIESRELATEDPHRASES"."ENTID" = "ENTITIES"."ENTID") INNER JOIN
 "EXISTING_PHRASES" ON ("ENTITIESRELATEDPHRASES"."PHRASEID" =
 "EXISTING_PHRASES"."PHRASEID") WHERE "ENTITIESRELATEDPHRASES"."ENTID" IN
 (74))


 pp str(c.query)
(SELECT  "ENTITIES"."MAINNAME", T4."MAINNAME" FROM "ENTITY_RELATION_ENTITY"
 INNER JOIN "ENTITIES" ON ("ENTITY_RELATION_ENTITY"."EID1" =
 "ENTITIES"."ENTID") INNER JOIN "ENTITIES" T4 ON
 ("ENTITY_RELATION_ENTITY"."EID2" = T4."ENTID") WHERE
 ("ENTITY_RELATION_ENTITY"."EID1" IN (74) AND
 "ENTITY_RELATION_ENTITY"."RELATIONID" = 8))

 (SELECT  "ENTITIES"."MAINNAME", T4."MAINNAME" FROM "ENTITY_RELATION_ENTITY"
 INNER JOIN "ENTITIES" ON ("ENTITY_RELATION_ENTITY"."EID1" =
 "ENTITIES"."ENTID") INNER JOIN "ENTITIES" T4 ON
 ("ENTITY_RELATION_ENTITY"."EID2" = T4."ENTID") WHERE
 ("ENTITY_RELATION_ENTITY"."EID1" IN (74) AND
 "ENTITY_RELATION_ENTITY"."RELATIONID" = 8))



'oble'

get_related_entities() =
['helium atom']

WordRelatedStrings('oble').get_related_phrases() =
 [('helium atom', 'helium'),
 ('helium atom', 'noble gas'),
 ('helium atom', 'noble gases')]

 WordRelatedStrings('oble').get_properties() =
 [('helium atom', 'covalent radius'),
 ('helium atom', 'ionization'),
 ('helium atom', 'van der waals radius'),
 ('helium atom', 'symbole'),
 ('helium atom', 'period (atom peroperty)'),
 ('helium atom', 'group (atom peroperty)'),
 ('helium atom', 'atomic number')]


 'viscosity of water'

 entities = [(water,['water,freshwater'])]



['covalent radius',
 'symbole',
 'symbole',
 'covalent radius',
 'covalent radius',
 'ionization',
 'ionization',
 'ionization',
 'van der waals radius',
 'period (atom peroperty)',
 'van der waals radius',
 'period (atom peroperty)',
 'van der waals radius',
 'group (atom peroperty)',
 'group (atom peroperty)',
 'symbole',
 'period (atom peroperty)',
 'group (atom peroperty)',
 'atomic number',
 'atomic number',
 'atomic number']

 ['atomic number',
 'covalent radius',
 'group (atom peroperty)',
 'ionization',
 'period (atom peroperty)',
 'symbole',
 'van der waals radius']






a = WordRelatedStrings('tom') # like atom - heydrogen atom - group (atom) - .....
s = a.get_related_entities_mainname()
d = a.get_related_words_for_scrapy_site_evaluation()
f = a.get_properties_for_site_scraping()

(Pdb) print(a)
<search_in_database.tools.WordRelatedStrings object at 0x000002437756CC18>
(Pdb) print(s)
['list of atoms',
 'atom',
 'atomic number',
 'hydrogen atom',
 'group (atom peroperty)',
 'period (atom peroperty)',
 'helium atom']
(Pdb) print(d)
['list of atoms',
 'atom',
 'atomic number',
 'hydrogen atom',
 'group (atom peroperty)',
 'period (atom peroperty)',
 'helium atom',
 'helium',
 'noble gas',
 'noble gases',
 'forManualSearch_Phrase',
 'hydrogen']
(Pdb) print(f)
['atomic number',
 'covalent radius',
 'group (atom peroperty)',
 'ionization',
 'period (atom peroperty)',
 'symbole',
 'van der waals radius']
