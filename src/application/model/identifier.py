import application.model.natural as natural
import application.model.string as string

'''uuid = {
'type':'string',
'min':64,
}

key = {
'type':'natural',
'min':1,
}

location = {
'type':'string',
'min':1,
}'''

identifier = (
    {'name':'identifier','model':natural.natural},
)

uuid = (
    {'name':'identifier','model':string.string},
)