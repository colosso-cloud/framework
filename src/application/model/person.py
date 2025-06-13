import application.model.name as name
import application.model.time as time
import application.model.string as string
import application.model.city as city
import application.model.contact as contact
import application.model.note as note

# User FirstName,MiddleName,LastName,CityOfBirth,PlaceOfBirth,DateOfBirth,Gender,Profession,CF,Title

person = (
    {'name':'contact','model':contact.contact,'remark':'contatti'},
    {'name':'cf','model':string.string,'remark':'cf'},
    {'type':note.note},
    {'name':'gender','model':string.string,'remark':'gender'},
    {'name':'first','model':name.name,'remark':'first_name'},
    {'name':'last','model':name.name,'remark':'last_name'},
    {'name':'date','model':time.time,'remark':'birth_date'},
    {'name':'city','model':city.city,'remark':'birth_town'},
    {'name':'province','model':city.city,'remark':'birth_province'},
)