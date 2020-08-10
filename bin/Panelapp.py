import os

import api
import dnanexus_nirvana


class Panel():
    def __init__(
        self, panel_id, version=None,
        confidence_level=None,
        assign_transcripts=False
    ):
        self.id = str(panel_id)
        self.version = version
        self.confidence_level = confidence_level
        self.query_panel_data()

        if assign_transcripts:
            self.assign_transcripts()

    def query_panel_data(self):
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

    def assign_transcripts(self):
        self.g2t = {}
        self.not_g2t = []
        project_id, file_id = dnanexus_nirvana.find_dnanexus_g2t()
        nirvana_g2t = dnanexus_nirvana.get_already_assigned_transcripts(
            project_id,
            file_id
        )

        for gene in self.get_genes():
            if gene in nirvana_g2t:
                selected_transcript = nirvana_g2t[gene]
                self.g2t[gene] = selected_transcript
            else:
                transcripts = dnanexus_nirvana.nirvana_transcripts(
                    gene,
                    False,
                    nirvana_g2t
                )

                if transcripts:
                    for transcript, field in transcripts.items():
                        if field["canonical"]:
                            selected_transcript = transcript
                            self.g2t[gene] = selected_transcript
                else:
                    self.not_g2t.append(gene)

        return self.g2t

    def write_panel(self, path="."):
        output_folder = "{}/panels".format(path)

        if not os.path.exists():
            os.mkdir(output_folder)
        else:
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)

        file_path = "{}/panels/{}".format(path, self.name)

        with open(file_path) as f:
            for gene, transcript in self.g2t.items():
                f.write("{}\t{}\n".format(gene, transcript))

    def get_latest_version(self):
        return Panel(panel_id=self.id).get_version()

    def get_version(self):
        return self.version

    def get_genes(self):
        return [
            gene["gene_data"]["hgnc_symbol"]
            for gene in self.genes if gene
        ]

    def get_g2t(self):
        if not self.g2t:
            self.assign_transcripts()

        return self.g2t

    def get_non_g2t(self):
        if not self.not_g2t:
            self.assign_transcripts()

        return self.not_g2t

    def get_data(self):
        return self.data

    def get_info(self):
        info = {
            "green_genes": 0,
            "entity_types": self.data["stats"]
        }

        for gene in self.genes:
            if gene["confidence_level"] == "3":
                info["green_genes"] += 1

        return info

    def __str__(self):
        return "{}: id={}; version={}; signedoff={}".format(
            self.name,
            self.id,
            self.version,
            self.signedoff
        )


if __name__ == "__main__":
    panel = Panel(panel_id=466, version=2.7, assign_transcripts=True)
    print(panel)
