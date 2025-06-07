import json
import sys

modules = {'flow': 'framework.service.flow'}
    
if sys.platform == 'emscripten':
    import js
    from js import supabase
    import pyodide


    async def backend_registration(supabase,**data):
        data_js = pyodide.ffi.to_js(data)
        print(data_js)
        user = await supabase.auth.signUp(data_js)
        user_dict = user.to_py()
        print(user_dict.get('error',None))
        print("SERVIZIO DI REGISTRAZIONE2")
        return user_dict.get('session',{}).get('access_token',None)
    
    async def backend_login(supabase,**data):
        print("SERVIZIO DI LOGIN2",data)
        data_js = pyodide.ffi.to_js(data)
        user = await supabase.auth.signInWithPassword(data_js)
        user_dict = user.to_py()
        print(user_dict,'login')
        return user_dict.get('data',{})
else:
    import supabase

    async def backend_registration(supabase,**data):
        user = supabase.auth.sign_up(data)

        return user.get('session',{}).get('access_token',None)
    
    async def backend_login(supabase,**data):
        user = supabase.auth.sign_in_with_password(data)
        data = user.dict()
        return data.get('session',{}).get('access_token',None)

class adapter:
    def __init__(self, **constants):
        self.config = constants['config']
        print(self.config,"config")
        self.url = self.config['url']
        self.key = self.config['key']
        
        if sys.platform == 'emscripten':
            print("Emscripten platform detected",dir(supabase))
            self.supabase =  supabase.createClient(self.url, self.key)
            print("Supabase client created",dir(self.supabase),dir(self.supabase.auth))
        else:
            self.supabase = supabase.create_client(self.url, self.key)
            
    @flow.asynchronous(outputs='transaction',managers=('messenger',))
    async def whoami(self, messenger, **data):
        result = await self.supabase.auth.getUser()
        result_dict = result.to_py()
        print(result_dict)
        if result_dict.get('error',None) != None:
            state = False
        else:
            state = True
        return {'state':state,'result':[result_dict.get('data',{}).get('user',{})]}
    
        

    async def registration(self,**data):
        try:
            return await backend_registration(self.supabase,**data)
        except Exception as e:
            print(f"Errore di autenticazione: {e}")

    async def logout(self,**data):
        try:
            print("Logout")
            await self.supabase.auth.signOut()
        except Exception as e:
            print(f"Errore di autenticazione: {e}")

    async def authenticate(self, **data):
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        #if not email or not password:
        #    await messenger.post(domain="error", message="Email e password sono obbligatori.")
        #    return None

        try:
            result = await backend_login(self.supabase, **data)
            #print(dir(result),result)
            return result
        except Exception as e:
            print(f"Errore di autenticazione: {e}")
            #await messenger.post(domain="error", message=f"Errore di autenticazione: {e}")
            return None
