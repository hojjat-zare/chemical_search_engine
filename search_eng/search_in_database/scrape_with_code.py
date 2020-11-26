import re


file = open('C:/Users/hojjat/crawler/search_eng/search_in_database/main properties.txt','rt')

a = []
for str in file.readlines():
    row = str.split('&&')
    a.append(row)
file.close()
j = []

# print(a[0][4])
a = a[2:-2]
for name in a:
    ss = []
    ss.append(re.findall('[A-Za-z]+',name[0])[0].lower()+' (_a_t_o_m_)')
    j.append(ss)

for i in range(len(a)):
    str = a[i][1]
    atom_number = re.findall('[0-9]+',str)[0]
    # print(str)
    j[i].append(atom_number)

for i in range(len(a)):
    str = a[i][2]
    str = re.findall('[0-9a-zA-Z]+',str)
    covalent = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    if(len(str) in [1,2,3,4,5]):
        covalent = re.findall('[0-9]+',str[0])
        if(len(covalent)>0):
            covalent = covalent[0]
        else:
            covalent = None
    elif(len(str) in [6]):
        covalent = str[1]
    else:
        covalent = str[6]
    j[i].append(covalent)


for i in range(len(a)):
    str = a[i][3]
    str = re.findall('[0-9a-zA-Z.]+',str)
    # print(str)
    if(len(str)>1):
        Ionization = str[1]
    else:
        Ionization = None
    j[i].append(Ionization)
# print(j)

for i in range(len(a)):
    str = a[i][4]
    str = re.findall('[0-9a-zA-Z.]+',str)
    vander = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    if(str[0]!='None'):
        vander = str[0]
    else:
        vander = None
    j[i].append(vander)


for i in range(len(a)):
    str = a[i][5]
    # print(str)
    str = re.findall('[0-9]+',str)
    if(len(str)>0):
        group = str[0]
    else:
        group = None
    j[i].append(group)

for i in range(len(a)):
    str = a[i][6]
    period = re.findall('[0-9]+',str)[0]
    j[i].append(period)

for i in range(len(a)):
    str = a[i][7]
    weight = re.findall('[0-9.]{3,}',str)
    if(len(weight)==0):
        weight = None
    elif(len(weight)==3):
        weight = weight[2]
    elif(len(weight)==1):
        weight = weight[0]
    else:
        weight = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    j[i].append(weight)


instance_type = 6
is_instance_of = 9
atom = 18
atomic_number = 19
covalent_rad = 43
Ionization = 44
vander_waals = 59
group = 139
period = 140
weight = 127
j = j[1:]
print(j)

# from .models import *
# def do_store():
#     for row in j:
#         entity = Entities(mainname='{}'.format(row[0]),enttypeid_id=instance_type)
#         entity.save()
#         ent_rel_ent = EntityRelationEntity(eid1=entity,relationid_id=is_instance_of,eid2_id=atom)
#         ent_rel_ent.save()
#         a1 = EntsIntegerPropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=atomic_number,drowid=0).update(dvalue=row[1])
#         a2 = EntsIntegerPropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=group,drowid=0).update(dvalue=row[5])
#         a3 = EntsIntegerPropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=period,drowid=0).update(dvalue=row[6])
#         a4 = EntsDoublePropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=covalent_rad,drowid=0).update(dvalue=row[2])
#         a5 = EntsDoublePropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=Ionization,drowid=0).update(dvalue=row[3])
#         a6 = EntsDoublePropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=vander_waals,drowid=0).update(dvalue=row[4])
#         a7 = EntsDoublePropsValues.objects.filter(prop_owner_eid=entity,prop_eid_id=weight,drowid=0).update(dvalue=row[7])


        # a1.save(force_update=True)
        # a2.save(force_update=True)
        # a3.save(force_update=True)
        # a4.save(force_update=True)
        # a5.save(force_update=True)
        # a6.save(force_update=True)
        # a7.save(force_update=True)
