import application.model.identifier as identifier
import application.model.time as time
import application.model.string as string
import application.model.integer as integer
#import domain.model.natural as natural

#INTERFACE = {'API':'API','CLI':'CLI','GUI':'GUI'}
#PLATFORM = {'WEB':'WEB','NATIVE':'NATIVE'}
#TARGET = {'MOBILE':'MOBILE','BROWSER':'BROWSER','DESKTOP':'DESKTOP','SERVER':'SERVER'}
#TYPE = {'INTERPRETED':'INTERPRETED', 'COMPILED':'COMPILED', 'HYBRID':'HYBRID'}
#LANGUAGES = {'PHP','PYTHON','RUST','SQL','C','JAVASCRIPT','GO'}
#FRAMEWORK = {'FLUTTER','GTK4','LARAVEL','PANDA'}

application = (
    {'model':identifier.identifier},
    {'name':'interfaces','type':dict(),'default':dict(),'allowed':['API','CLI','GUI']},
    {'name':'platform','type':string.string,'allowed':['WEB','NATIVE']},
    {'name':'target','type':string.string,'allowed':['MOBILE','BROWSER','DESKTOP','SERVER']},
    {'name':'args','type':[],'default':[]},
    {'name':'policies','type':dict(),},
)