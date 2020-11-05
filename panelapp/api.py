import json

import requests


def build_url(path: list, param: dict = None):
    """ Builds external url path with parameters

    Args:
        path (list): List with path that is going to be separated with "/"
        param (dict): Dict containing parameters (key=param_name, value=param_value)

    Returns:
        str: External URL to pass to the base URL for the API call
    """

    suffix = "/".join(path)
    ext_url = "{}".format(suffix)

    if param:
        used_param = {key: val for key, val in param.items() if val}

        if used_param:
            parameters = "&".join(
                ["{}={}".format(key, val) for key, val in used_param.items()]
            )
            ext_url = "{}?{}".format(suffix, parameters)

    return ext_url


def get_panelapp_response(ext_url: str = None, full_url: str = None):
    """ Make an API query

    Args:
        ext_url (str, optional): External path for the URL to add to the base URL. Defaults to None.
        full_url (str, optional): Full url to use for the API call. Defaults to None.

    Returns:
        dict: Data from the API call
    """

    if full_url:
        url = full_url
    else:
        url = "https://panelapp.genomicsengland.co.uk/api/v1/{}".format(
            ext_url
        )

    for i in range(0, 5):
        try:
            request = requests.get(url, headers={"Accept": "application/json"})
        except Exception as e:
            print("Something went wrong: {}".format(e))
        else:
            if request.ok:
                data = json.loads(request.content.decode("utf-8"))
                return data
            else:
                print("Error {} for URL: {}".format(request.status_code, url))
                return None

    return None


def get_full_results_from_API(data: dict):
    """ Get all the results from the API call

    Panelapp API doesn't show all the results.
    Instead, it returns another URL to point to the next page.
    To fix that, this function makes API calls while there's a pagination url.

    Args:
        data (dict): Dict output from the API call

    Returns:
        list: Data of every page
    """

    res = []

    while True:
        res.append(data["results"])

        if not data["next"]:
            break
        else:
            data = get_panelapp_response(full_url=data["next"])

    flat_list = []

    for sublist in res:
        for item in sublist:
            flat_list.append(item)

    return flat_list
