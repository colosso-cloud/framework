import application.model.user as user
import application.model.identifier as identifier
import application.model.person as person
import application.model.name as name
import application.model.payment as payment
#import domain.model.contact as contact

x = (
    ('id',('Integer', 'primary_key')),
    ('name',('String')),
    ('subject_type',('String')),
    ('first_name',('String')),
    ('last_name',('String')),
    ('address1',('String')),
    ('city',('String')),
    ('prov',('String')),
    ('zip',('String')),
    ('piva',('String')),
    ('cf',('String')),
    ('phone',('String')),
    ('cell',('String')),
    ('email',('String')),
    ('payment_method',('String')),
    ('codice_sdi',('String')),
    ('codice_cig',('String')),
    ('legal_representative',('String')),
    ('iban',('String')),
    ('legal_representative_cf',('String')),
    #('birth_date',('DateTime')),
    ('birth_town',('String')),
    ('birth_province',('String')),
)

# Type | Length | Value
client = (
    {'model':identifier.identifier},
    {'model':name.name},
    {'name':'person','model':person.person},
    {'name':'payment','type':payment.payment},
)

'''client = (
    (('iban',), None),
    (('method',), None),# payment_method
    ('identifier',('Integer', 'primary_key')),
    ('name',('String')),
    #('subject_type',('String')),
    #('payment_method',('String')),
    #('codice_sdi',('String')),
    #('codice_cig',('String')),
    #('legal_representative',('String')),
    #('iban',('String')),
    #('legal_representative_cf',('String')),
)'''