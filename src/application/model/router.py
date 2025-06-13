import application.model.user as user
import application.model.identifier as identifier
import application.model.person as person
import application.model.name as name
#import domain.model.contact as contact


# Type | Length | Value
router = (
    {'name':'CPEID','model':identifier.identifier},
    {'name':'state','type':''},
    {'name':'name','type':''},
    {'name':'location','type':''},
    {'name':'manufacturer','type':''},
    {'name':'model','type':''},
    {'name':'version','type':''},
    {'name':'ip','type':''},
    {'name':'last','type':''},
)