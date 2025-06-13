modules = {'flow':'framework.service.flow'}

import js
@flow.asynchronous(managers=('messenger','presenter','tester'))
async def preview(messenger,presenter,tester,**constants):
    id = constants.get('id','')
    code = constants.get('code','')
    component = await presenter.component(name=id)
    editor = await presenter.component(name=code)
    code_value = editor['block-editor-'].getValue()
    test_value = editor['block-test-'].getValue()
    a = await tester.unittest(test_value)
    #print(component,test_value,a)
    #print("preview",id)
    #print('PREVIEW:',component)
    if a['setup']:
        await presenter.Upcomponent(name=id,value=a['setup'])
        view = await presenter.rebuild(id=id,view=a['setup'].get('view',''),data={'code':code_value})
    else:
        print('view:',component.get('view',''))
        view = await presenter.rebuild(id=id,view=component.get('view',''),data={'code':code_value})