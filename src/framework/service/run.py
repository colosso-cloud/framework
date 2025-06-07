import asyncio
import sys

loader = language.load_main(language,area="framework",service='service',adapter='loader')

#modules = {'loader': 'framework.service.loader','language': 'framework.service.language'}

import os
import requests
import hashlib

def get_remote_file_sha(url):
    response = requests.get(url)
    if response.status_code == 200:
        return hashlib.sha256(response.content).hexdigest(), response.content
    return None, None

def get_local_file_sha(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def sync_directory_recursive(api_url, local_dir):
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception("GitHub API error:", response.json())
    
    files = response.json()

    for item in files:
        if item['type'] == 'dir':
            # Ricorsione per le sottocartelle
            sub_local_dir = os.path.join(local_dir, item['name'])
            sync_directory_recursive(item['url'], sub_local_dir)
        elif item['type'] == 'file':
            file_path = os.path.join(local_dir, item['name'])
            remote_sha, remote_content = get_remote_file_sha(item['download_url'])
            local_sha = get_local_file_sha(file_path)

            if local_sha != remote_sha:
                print(f"[Updating] {file_path}")
                os.makedirs(local_dir, exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(remote_content)
            else:
                print(f"[OK] {file_path} is up to date.")
        else:
            print(f"[Skipping] {item['type']}: {item['path']}")

def sync_github_repo(local_base_dir, github_user, repo, branch='main'):
    api_url = f"https://api.github.com/repos/{github_user}/{repo}/contents/src?ref={branch}"
    sync_directory_recursive(api_url, local_base_dir)

def build():
    pass

#@flow.synchronous(managers=('tester',))
def application(tester=None, **constants):
    try:
        if tester and '--test' in constants.get('args',[]):
            tester.run()
        if '--update' in constants.get('args',[]):
            sync_github_repo("src", "colosso-cloud", "framework", "main")
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        event_loop.create_task(loader.bootstrap())
        event_loop.run_forever()
    except KeyboardInterrupt:
        # Interruzione manuale con Ctrl+C
        #asyncio.create_task(messenger.post(msg="Interruzione da tastiera (Ctrl + C)."))
        pass
    except Exception as e:
        # Gestione di altre eccezioni con nome file, modulo e numero di riga
        exc_type, exc_value, exc_traceback = sys.exc_info()
        last_frame = exc_traceback.tb_frame
        filename = last_frame.f_code.co_filename
        module = last_frame.f_code.co_name
        line_number = exc_traceback.tb_lineno
        print(f"RUN -Errore generico: {e}")
        print(f"File: {filename}, Modulo: {module}, Linea: {line_number}")
    finally:
        # Chiusura del loop
        '''if event_loop.is_running():
            event_loop.stop()
        event_loop.close()'''
        #logging.info(msg="Event loop chiuso.")
        pass