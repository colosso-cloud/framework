from typing import NewType

'''
(code:natural<key>)
(title)
(comment)
(state)
(target:<(Customer)|(user)>)
(severity)
(data:string,<open>)
(data:string,<close>)
(area)
(assigned:string<user>)
(contacts:list<email,phone,address>)
'''

# User Name,Comment,State,target:user|customer,tenure
version = NewType('version', int,int,int)