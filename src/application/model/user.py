import application.model.password as password
import application.model.name as name
import application.model.string as string
import application.model.identifier as identifier
import application.model.url as url
'''
# User
(code:natural)
(username)
(roles:array[enum])
(permissions:array[enum])
(active:boolean)
'''

'''user = (
    (('company','person'), None),
    (('name',), 'state'),#username
    (('password',), 'state'),
)'''

user = (
    {'model':identifier.identifier},
    {'name':'username','model':name.name},
    {'model':password.password},
    {'name':'role','model':string.string},
    {'avatar':'role','model':url.url},
)