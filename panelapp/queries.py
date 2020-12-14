from .api import get_panelapp_response, get_full_results_from_API
from .Panelapp import Panel


def get_all_signedoff_panels(confidence_level: str = "3"):
    """ Return list of signedoff panel objects

    Args:
        confidence_level (str, optional): Specify. Defaults to "3".

    Returns:
        list: List of panel objects
    """

    panels = {}

    signedoff_panels = get_panelapp_response(ext_url="panels/signedoff")
    res = get_full_results_from_API(signedoff_panels)

    for data in res:
        panels[data["id"]] = Panel(
            panel_id=data["id"],
            version=data["version"],
            confidence_level=confidence_level
        )

    return panels


def compare_versions(original_panel: Panel, compare_version: str):
    """ Return matches and differences in the genes in the version given

    Args:
        original_panel (Panel object): Panel object to compare
        compare_version (str): Version of the Panel object to compare to

    Returns:
        tuple: Tuple of sets with genes matched and not matched
    """

    new_panel = Panel(
        panel_id=original_panel.id,
        version=compare_version,
        confidence_level=original_panel.confidence_level
    )

    original_genes = original_panel.get_hgnc_ids(1, 2, 3)
    compare_genes = new_panel.get_hgnc_ids(1, 2, 3)

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

    signedoff_panel = get_panelapp_response(
        ext_url="panels/signedoff/{}".format(panel_id)
    )
    return signedoff_panel


def get_all_panels():
    """ Returns all panels

    Returns:
        dict: All panels in Panelapp
    """

    all_panels = {}
    data = get_panelapp_response(ext_url="panels")
    panels = get_full_results_from_API(data)

    for panel in panels:
        all_panels[panel["id"]] = Panel(panel_id=panel["id"])

    return all_panels
