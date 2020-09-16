import os

from .api import build_url, get_panelapp_response


class Panel():
    def __init__(
        self, panel_id: str, version: str = None,
        confidence_level: str = "3",
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

    def query_panel_data(self):
        """ Query data to Panelapp API and assign data to attributes of the panel object 

        Return:
            None: if the panel wasn't found
        """

        path = ["panels", self.id]
        param = {"version": self.version}

        url = build_url(path, param)
        data = get_panelapp_response(url)

        if data:
            self.data = data
            self.name = self.data["name"]
            self.hash_id = self.data["hash_id"]
            self.version = self.data["version"]
            self.relevant_disorders = self.data["relevant_disorders"]
            self.set_genes()

            if "signed_off" in self.data:
                self.signedoff = self.data["signed_off"]
            else:
                self.signedoff = False

    def update_version(self, version: str, confidence_level: str = "3"):
        """ Update the version and confidence level for the Panel object

        Args:
            version (str): Version to update to
            confidence_level (str, optional): Confidence level. Defaults to "3".
        """

        self.version = version
        self.confidence_level = confidence_level
        self.query_panel_data()

    def write(self, path: str = None):
        """ Write gene to transcript file

        Args:
            path (str, optional): Path where to write the panel. Defaults to None.
        """

        if not path:
            output_folder = "panels"
        else:
            output_folder = "{}".format(path)

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        else:
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)

        panel_name = self.name.replace(" - ", " ")
        panel_name = panel_name.replace("-", " ")
        panel_name = panel_name.replace("/", " ")
        panel_name = " ".join(panel_name.split(" "))

        file_path = "{}/{}_{}.tsv".format(
            output_folder, panel_name, self.version
        )

        with open(file_path, "w") as f:
            for gene in self.get_genes():
                f.write("{}\t{}_{}\t{}\n".format(
                    self.name, self.name, self.version, gene
                ))

    def get_name(self):
        """ Return the panel name

        Returns:
            str: Panel name
        """

        return self.name

    def get_id(self):
        """ Return panel id

        Returns:
            str: Panel id
        """

        return self.id

    def get_hash_id(self):
        """ Return hash_id for the panel

        Returns:
            str: Hash id
        """

        return self.hash_id

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

    def get_relevant_disorders(self):
        """ Return list of relevant disorders

        Returns:
            list: Relevant disorders
        """

        return self.relevant_disorders

    def set_genes(self):
        """ Set the genes to their appropriate confidence level """

        self.genes = {}

        for gene in self.data["genes"]:
            if gene["confidence_level"] == "3":
                self.genes.setdefault("3", []).append(
                    gene["gene_data"]["hgnc_symbol"]
                )
            elif gene["confidence_level"] == "2":
                self.genes.setdefault("2", []).append(
                    gene["gene_data"]["hgnc_symbol"]
                )
            elif gene["confidence_level"] == "1":
                self.genes.setdefault("1", []).append(
                    gene["gene_data"]["hgnc_symbol"]
                )
            elif gene["confidence_level"] == "0":
                self.genes.setdefault("0", []).append(
                    gene["gene_data"]["hgnc_symbol"]
                )

    def get_genes(self, *confidence_levels: str):
        """ Return list of genes
        Can type 1,2,3 to get genes with appropriate confidence level to return

        Returns:
            list: List of genes
        """

        if confidence_levels:
            genes_to_return = []

            for level in confidence_levels:
                genes_to_return.append(self.genes[str(level)])

            genes_to_return = [
                gene
                for gene_list in genes_to_return
                for gene in gene_list
            ]
        else:
            genes_to_return = self.genes[self.confidence_level]

        return genes_to_return

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
            "green_genes": len(self.genes["3"]),
            "entity_types": self.data["stats"]
        }

        return info

    def is_signedoff(self):
        """ Return whether the panel is signedoff
        Can be False if not signedoff or a date in (YYYY-MM-DD format)

        Returns:
            (bool, str): Signedoff date or bool
        """

        return self.signedoff

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
