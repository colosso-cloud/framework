modules = {'flow':'framework.service.flow'}

@flow.asynchronous(managers=('messenger','presenter'))
async def messenger(messenger,presenter,**constants):
    identifier = constants.get('identifier','')
    message_id = constants.get('message','')
    component = await presenter.component(name=identifier)
    for message in component['messenger']:
        if message['identifier'] == message_id:
            component['messenger'].remove(message)
    print(component['messenger'])