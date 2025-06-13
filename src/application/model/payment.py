import application.model.name as name
import application.model.time as time
import application.model.string as string
import application.model.city as city
import application.model.contact as contact
import application.model.note as note

# User FirstName,MiddleName,LastName,CityOfBirth,PlaceOfBirth,DateOfBirth,Gender,Profession,CF,Title

payment = (
    {'name':'method','type':string.string},
    {'name':'iban','type':string.string},
)