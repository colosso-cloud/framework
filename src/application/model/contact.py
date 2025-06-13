import application.model.string as string
import application.model.url as url
import application.model.location as location

contact = (
    {'name':'location','model':location.location,'remark':'location'},
    {'name':'remark','model':string.string,'remark':'comment'},
    {'name':'phone','model':string.string,'remark':'phone'},
    {'name':'cellular','model':string.string,'remark':'phone'},
    {'name':'email','model':string.string,'remark':'email'},
    {'name':'website','model':url.url,'remark':'website'},
)