import application.model.identifier as identifier
import application.model.time as time
import application.model.string as string
import application.model.integer as integer
#import domain.model.natural as natural

event = (
    {'model':identifier.identifier},
    {'model':time.time},
    {'name':'domain','model':string.string},
    {'name':'action','model':string.string},
    {'name':'payload','model':string.string},
)