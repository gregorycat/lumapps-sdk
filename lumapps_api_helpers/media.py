import logging

from lumapps_api_helpers.exceptions import BadRequestException

def list_medias(api, lang, **params):
    # type (ApiClient, str, dict) -> (list)
    """List all the medias.

        Args:
            api (object): The ApiClient instance used for request.
            lang (str): the lang. Defaults to english (en).
            ``**params``: optional  dictionary of search parameters as defined in https://api.lumapps.com/docs/media/list.

        Returns:
            list: A list containing all the medias.
    """ 
    params["lang"] = lang if lang else 'en'
    return api.get_call("media", "list", **params)

def upload_file(api, f):
    # type: (ApiClient, list[str]) -> (dict)
    """Upload a file to the googleusercontent of the ApiClient.

        Args:
            api (object): The ApiClient instance used for request.
            files (list[str]): A list of paths to the files to upload.
        
        Returns:
            list[dict]: The post request return.
    """
    upload_url = api.get_call('file', 'uploadUrl')['uploadUrl']
    response = api.get_authed_session().post(upload_url, files=[('files', open(f, 'rb'))])
    if response.status_code != 200:
        logging.error("Upload file {} failed. Response content was {}.".format(f, reponse.content))
        raise Exception(str(response.content))
    uploaded_file = response.json()
    return uploaded_file

def save_media(api, media):
    # type: (ApiClient, dict) -> None
    """Save a media.

        Args:
            api (object): The ApiClient instance used to request.
            media (dict): the media to save.
    """
    api.get_call("media", "save", body = media)

def uploaded_to_media(uploaded_file, instance, lang, name=None):
    # type: (dict, str, str, str) -> dict
    """Transform an uploaded file (post reponse) into a minimal media.

        Args:
            uploaded_file (dict): The post reponse returned after uploading a file.
            lang (str): the lang associated to the file.
            instance (str): the instance where the file will live (and be saved).
        
        Returns:
            dict: A media ressource as described in https://api.lumapps.com/docs/output/_schemas/media.
    """
    media = {}
    media["instance"] = instance
    media['content'] = [{
                'ext': uploaded_file.get('ext'),
                'height': uploaded_file.get('height', 0),
                'width': uploaded_file.get('width', 0),
                'lang': lang,
                'mimeType': uploaded_file.get('mimeType'),
                'name': name or uploaded_file.get('name'),
                'url': uploaded_file.get('url'),
                'servingUrl': uploaded_file.get('url'),
                'size': uploaded_file.get('fileSize'),
                'type': uploaded_file.get('type'),
                'value': uploaded_file.get('blobKey'),
            }]
    media['name'] = {lang: name or uploaded_file.get('name')}
    return media

def upload_and_save(api, instance, files, langs=None, names=None):
    # type: (ApiClient, str, list[str], list[str], list[str]) -> None
    """Upload and save a list of 1 or several files to the specified lumapps site (instance).

        Args:
            api (object): The ApiClient instance used to request.
            instance (str): the instance where to save the files
            files (list[str]): A list of the paths to the files to save.
            langs (list[str], optional): A list containing the lang associated to each file. Defaults to english.
            name (list[str], optional): A list containing the name associated to each file. Defaults to the filename.
    """
    langs = ['en']*len(files) if langs is None else langs
    names = [None]*len(files) if names is None else names
    for f, lang, name in zip(files, langs, names):
        uploaded_file = upload_file(api, f)
        logging.info("File {} uploaded !")
        media = uploaded_to_media(uploaded_file, instance, lang, name)
        save_media(api, media)
        logging.info("File : {} saved !".format(f))
        print("File : {} saved !".format(f))


        

    