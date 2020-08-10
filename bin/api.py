import json
import sys

import requests


def build_url(path, param):
    suffix = "/".join(path)
    ext_url = "{}".format(suffix)
    used_param = {key: val for key, val in param.items() if val}

    if used_param:
        parameters = "&".join(
            ["{}={}".format(key, val) for key, val in used_param.items()]
        )
        ext_url = "{}?{}".format(suffix, parameters)

    return ext_url


def get_panelapp_response(ext_url=None, full_url=None):
    """ Get response from swagger panelapp api """

    if full_url:
        url = full_url
    else:
        url = "https://panelapp.genomicsengland.co.uk/api/v1/{}".format(
            ext_url
        )

    try:
        request = requests.get(url, headers={"Accept": "application/json"})
    except Exception as e:
        print("Something went wrong: {}".format(e))
        sys.exit(-1)
    else:
        if request.ok:
            data = json.loads(request.content.decode("utf-8"))
            return data
        else:
            print("Error {} for URL: {}".format(request.status_code, url))
            sys.exit(-1)


def get_full_results_from_API(data):
    """ Get all the results

    Panelapp API doesn't show all the results
    To fix that, this function makes API calls while there's a pagination url
    Return the data of every page
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
