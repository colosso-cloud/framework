modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter'))
async def builder(messenger,presenter,**constants):
    url = f'application/view/component/{constants["component"]}.xml'
    view = await presenter.builder(url=url)
    element = js.document.getElementById(constants['target'])
    element.appendChild(view)