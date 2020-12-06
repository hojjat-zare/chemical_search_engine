import re
aaa = 'movie tickets booking movie in online'
bbb = 'movie tickets booking movie in online'
re.subn('ov', '~*' , aaa)
b = re.subn('ov', '~*' , bbb, flags = re.IGNORECASE)

print(b)
print(aaa)
print(bbb)