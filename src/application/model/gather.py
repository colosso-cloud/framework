import application.model.user as user
import application.model.identifier as identifier
import application.model.natural as natural
import application.model.string as string
#import domain.model.contact as contact

# Type | Length | Value
#(['model'=>$pieces[1],'rows'=>$this->perPage,'page'=>$this->currentPage,'search'=>$this->query,'filter'=>$this->filtered,'orderby'=>$this->sortField,'sort'=>$this->sortAsc ? 'asc' : 'desc']);
gather = (
    {'name':'model','model':string.string},
    {'name':'identifier','model':string.string},
    {'name':'sort','model':string.string},
    {'name':'orderby','model':string.string},
    {'name':'rows','model':string.string},
    {'name':'page','model':string.string},
    {'name':'filter','model':string.string},
    {'name':'search','model':string.string},
)

