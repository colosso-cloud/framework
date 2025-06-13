modules = {'flow':'framework.service.flow'}

@flow.asynchronous(managers=('defender','presenter'))
async def login(defender,presenter,**constants):
    session = await defender.authenticate(ip='1111',identifier='asdasd',**constants)
    print(session,'login')
    if session:
        await presenter.navigate(url='/profile')