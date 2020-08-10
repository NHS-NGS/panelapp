import api
import Panelapp


def get_all_signedoff_panels():
    """ Get the panels IDs and versions of the signedoff panels

    The API doesn't allow much with the signedoff panels
    So need to get the version to use the manipulate the panel
    """

    panels = []

    signedoff_panels = api.get_panelapp_response(ext_url="panels/signedoff")
    res = api.get_full_results_from_API(signedoff_panels)

    for data in res:
        panels.append(Panelapp.Panel(id=data["id"], version=data["version"]))

    return panels


def compare_versions(original_panel, compare_version):
    new_panel = Panelapp.Panel(
        panel_id=original_panel.id,
        version=compare_version,
        confidence_level=original_panel.confidence_level
    )

    original_genes = original_panel.get_genes()
    compare_genes = new_panel.get_genes()

    matches = set(original_genes).intersection(set(compare_genes))
    difference = set(original_genes).symmetric_difference(set(compare_genes))

    return (matches, difference)


def get_signedoff_panel(panel_id):
    signedoff_panel = api.get_panelapp_response(
        ext_url="panels/signedoff/{}".format(panel_id)
    )
    return signedoff_panel
