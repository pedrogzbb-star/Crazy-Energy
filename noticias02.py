# uv pip install GoogleNews pydrive2 pandas
from GoogleNews import GoogleNews
import pandas as pd
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

KEYWORDS_FILE = 'keywords.txt'
LOCAL_FOLDER = 'tfm'
LOCAL_CSV = os.path.join(LOCAL_FOLDER, 'noticias_energia_keywords.csv')
DRIVE_FOLDER_NAME = 'tfm'
CREDENTIALS_FILE = 'credentials.json'
CREDENTIALS_STORE = 'creds.json'

def load_keywords(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def build_query(keywords):
    keywords_quoted = ['"{}"'.format(k) if ' ' in k else k for k in keywords]
    return 'energía AND (' + ' OR '.join(keywords_quoted) + ')'

def fetch_news(query, pages=6):
    googlenews = GoogleNews(lang='es', region='ES')
    googlenews.set_time_range('01/01/2024', '31/12/2024')
    googlenews.search(query)

    all_results = []
    for page in range(1, pages + 1):
        googlenews.getpage(page)
        all_results.extend(googlenews.result())

    seen = set()
    unique = []
    for item in all_results:
        link = item.get('link')
        if link and link not in seen:
            seen.add(link)
            unique.append(item)

    return unique

def save_local_csv(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return path

def auth_drive():
    gauth = GoogleAuth()
    gauth.settings['client_config_file'] = CREDENTIALS_FILE
    gauth.LoadCredentialsFile(CREDENTIALS_STORE)
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(CREDENTIALS_STORE)
    return GoogleDrive(gauth)

def get_or_create_drive_folder(drive, folder_name):
    query = (
        "title = '{name}' and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    ).format(name=folder_name)
    folder_list = drive.ListFile({'q': query}).GetList()
    if folder_list:
        return folder_list[0]
    folder = drive.CreateFile({
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    })
    folder.Upload()
    return folder

def upload_to_drive(drive, local_path, parent_folder):
    file_drive = drive.CreateFile({
        'title': os.path.basename(local_path),
        'parents': [{'id': parent_folder['id']}]
    })
    file_drive.SetContentFile(local_path)
    file_drive.Upload()
    return file_drive['id']

def main():
    keywords = load_keywords(KEYWORDS_FILE)
    if not keywords:
        raise ValueError(f"El archivo {KEYWORDS_FILE} está vacío")

    query = build_query(keywords)
    print('Consulta:', query)

    results = fetch_news(query, pages=6)
    if not results:
        print('No se encontraron resultados.')
        return

    local_path = save_local_csv(results, LOCAL_CSV)
    print(f'Archivo guardado localmente en: {local_path}')

    drive = auth_drive()
    folder = get_or_create_drive_folder(drive, DRIVE_FOLDER_NAME)
    file_id = upload_to_drive(drive, local_path, folder)
    print(f'Archivo subido a Google Drive en carpeta "{DRIVE_FOLDER_NAME}", fileId={file_id}')

if __name__ == '__main__':
    main()
