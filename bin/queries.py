import api
import Panelapp


def get_all_signedoff_panels():
    """ Return list of signedoff panel objects

    Returns:
        list: List of panel objects
    """

    panels = []

    signedoff_panels = api.get_panelapp_response(ext_url="panels/signedoff")
    res = api.get_full_results_from_API(signedoff_panels)

    for data in res:
        panels.append(Panelapp.Panel(id=data["id"], version=data["version"]))

    return panels


def compare_versions(original_panel: Panelapp.Panel, compare_version: str):
    """ Return matches and differences in the genes in the version given

    Args:
        original_panel (Panel object): Panel object to compare
        compare_version (str): Version of the Panel object to compare to

    Returns:
        tuple: Tuple of sets with genes matched and not matched
    """

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


def get_signedoff_panel(panel_id: str):
    """ Return data of signedoff panel

    Args:
        panel_id (str): Panel id

    Returns:
        dict: Data of the panel
    """
    signedoff_panel = api.get_panelapp_response(
        ext_url="panels/signedoff/{}".format(panel_id)
    )
    return signedoff_panel
