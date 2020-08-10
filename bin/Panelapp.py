import os

import api
import dnanexus_nirvana


class Panel():
    def __init__(
        self, panel_id: str, version: str = None,
        confidence_level: str = None,
        assign_transcripts: str = False
    ):
        """ Initialise Panel object, call the PanelApp API to get data

        Args:
            panel_id (str): Panel id
            version (str, optional): Version of the panel to get. Defaults to None.
            confidence_level (str, optional): Confidence level for the genes of the panel. Defaults to None.
            assign_transcripts (str, optional): File path to the GFF. Defaults to False.
        """

        self.id = str(panel_id)
        self.version = version
        self.confidence_level = confidence_level
        self.query_panel_data()

        if assign_transcripts:
            self.assign_transcripts(assign_transcripts)

    def query_panel_data(self):
        """ Query data to Panelapp API and assign data to attributes of the panel object """

        path = ["panels", self.id]
        param = {
            "version": self.version,
            "confidence_level": self.confidence_level
        }

        url = api.build_url(path, param)
        self.data = api.get_panelapp_response(url)
        self.name = self.data["name"]
        self.version = self.data["version"]
        self.genes = self.data["genes"]

        if "signed_off" in self.data:
            self.signedoff = self.data["signed_off"]
        else:
            self.signedoff = False

    def assign_transcripts(self, refseq_gff: str):
        """ Assign transcripts to the genes of the panel

        Args:
            refseq_gff (str): File path to the GFF

        Returns:
            dict: Dict linking genes and transcripts
        """

        self.g2t = {}
        self.not_g2t = []
        project_id, file_id = dnanexus_nirvana.find_dnanexus_g2t()
        nirvana_g2t = dnanexus_nirvana.get_already_assigned_transcripts(
            project_id,
            file_id
        )
        nirvana_data_dict = dnanexus_nirvana.get_nirvana_data_dict(refseq_gff)

        for gene in self.get_genes():
            if gene in nirvana_g2t:
                selected_transcript = nirvana_g2t[gene]
                self.g2t[gene] = selected_transcript
            else:
                transcripts = dnanexus_nirvana.nirvana_transcripts(
                    gene,
                    False,
                    nirvana_data_dict
                )

                if transcripts:
                    for transcript, field in transcripts.items():
                        if field["canonical"]:
                            selected_transcript = transcript
                            self.g2t[gene] = selected_transcript
                else:
                    self.not_g2t.append(gene)

        return self.g2t

    def write_panel(self, path: str = None):
        """ Write gene to transcript file

        Args:
            path (str, optional): Path where to write the panel. Defaults to None.
        """

        if not path:
            output_folder = "/panels"
        else:
            output_folder = "{}".format(path)

        if not os.path.exists():
            os.mkdir(output_folder)
        else:
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)

        file_path = "{}/{}".format(output_folder, self.name)

        with open(file_path) as f:
            for gene, transcript in self.g2t.items():
                f.write("{}\t{}\n".format(gene, transcript))

    def get_latest_version(self):
        """ Return latest possible version of current Panel object

        Returns:
            str: Version of the latest version
        """

        return Panel(panel_id=self.id).get_version()

    def get_version(self):
        """ Return version of current Panel object

        Returns:
            str: Version of the current Panel object
        """

        return self.version

    def get_genes(self):
        """ Return list of genes of the Panel object

        Returns:
            list: List of genes
        """
        return [
            gene["gene_data"]["hgnc_symbol"]
            for gene in self.genes if gene
        ]

    def get_g2t(self):
        """ Return g2t dict

        Returns:
            dict: Dict of gene -> transcript
        """

        try:
            self.g2t
        except AttributeError as e:
            print("{}. Please run assign_transcripts(gff_file)".format(e))
        else:
            return self.g2t

    def get_non_g2t(self):
        """ Return list of genes with no transcript

        Returns:
            list: List of genes with no transcript
        """

        try:
            self.non_g2t
        except AttributeError as e:
            print("{}. Please run assign_transcripts(gff_file)".format(e))
        else:
            return self.non_g2t

    def get_data(self):
        """ Return the full data of the panel. Used for debug mainly

        Returns:
            dict: Dict of all the data of the panel
        """

        return self.data

    def get_info(self):
        """ Return the amount of green genes and types of elements in the panel

        Returns:
            dict: Dict with green_genes and entity_types keys to access data
        """
        info = {
            "green_genes": 0,
            "entity_types": self.data["stats"]
        }

        for gene in self.genes:
            if gene["confidence_level"] == "3":
                info["green_genes"] += 1

        return info

    def __str__(self):
        """ Return a string with basic info on the panel

        Returns:
            str: String with panel name, id, version and signedoff date
        """

        return "{}: id={}; version={}; signedoff={}".format(
            self.name,
            self.id,
            self.version,
            self.signedoff
        )
