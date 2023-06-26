import pytest

from panelapp.queries import get_signedoff_panel


class TestGetSignedOffPanel:
    """
    Note that these tests currently use real API calls, instead of mock data.
    Therefore they will need updating as the contents of Panelapp change.
    """
    def test_real_panel(self):
        """
        A real signed-off panel ID for Stickler Syndrome as of 26th June 2023
        """
        return_panel_id_3 = \
        {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
            "id": 3,
            "name": "Stickler syndrome",
            "stats": {
                "number_of_strs": 0,
                "number_of_genes": 11,
                "number_of_regions": 0
            },
            "types": [
                {
                "name": "Rare Disease 100K",
                "slug": "rare-disease-100k",
                "description": "Rare Disease 100K"
                },
                {
                "name": "GMS Rare Disease Virtual",
                "slug": "gms-rare-disease-virtual",
                "description": "This is a panel for the Genomic Medicine Service for an exome/genome/panel based test that requires a virtual gene panel for rare disease in the Test Directory."
                },
                {
                "name": "GMS Rare Disease",
                "slug": "gms-rare-disease",
                "description": "This panel type is used for GMS panels that are not virtual (i.e. could be a wet lab test)"
                },
                {
                "name": "GMS signed-off",
                "slug": "gms-signed-off",
                "description": "This panel has undergone review by a NHSE GMS disease specialist group and processes to be signed-off for use within the GMS."
                }
            ],
            "status": "public",
            "hash_id": "554a0ac9bb5a167e4ccd1ec1",
            "version": "4.0",
            "disease_group": "Skeletal disorders",
            "version_created": "2023-03-22T15:38:28.046827Z",
            "disease_sub_group": "Skeletal dysplasias",
            "relevant_disorders": [
                "R45"
            ],
            "signed_off": "2023-03-22"
            }
        ]
        }

        assert get_signedoff_panel(3) == return_panel_id_3


    def test_nonexistent_panel_returns_error(self):
        """
        None is returned for nonsense panel ID
        """
        panel_id = "a_nonsense_string"

        assert get_signedoff_panel(panel_id) == None



