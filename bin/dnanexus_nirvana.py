import gzip

import dxpy

import hgnc_queries


def get_nirvana_data_dict(nirvana_refseq: str):
    """ Return dict of gene2transcript

    Args:
        nirvana_refseq (str): Path to the nirvana gff refseq

    Returns:
        dict: Dict of gene2transcript
    """

    nirvana_tx_dict = {}

    with gzip.open(nirvana_refseq) as nir_fh:
        for line in nir_fh:
            gff_gene_name = None
            gff_transcript = None
            gff_tag = ""

            fields = line.decode("utf-8").strip().split("\t")
            record_type = fields[2]

            if not record_type == "transcript":
                continue

            info_field = fields[8]
            info_fields = info_field.split("; ")

            for field in info_fields:
                key, value = field.split(" ")

                if key == "gene_name":
                    gff_gene_name = value.replace('"', '').upper()
                elif key == "transcript_id" and value.startswith('"NM_'):
                    gff_transcript = value.replace('"', '')
                elif key == "tag":
                    gff_tag = value.replace('"', '')

            if gff_gene_name and gff_transcript:
                chrom = fields[0].replace("chr", "")
                start, end = fields[3:5]
                canonical = gff_tag
                nirvana_tx_dict.setdefault(gff_gene_name, {})[
                    gff_transcript
                ] = {
                    "chrom": chrom,
                    "start": start,
                    "end": end,
                    "canonical": canonical
                }

    return nirvana_tx_dict


def nirvana_transcripts(
    gene_name: str, verbose: bool = True, nirvana_data_dict: dict = None
):
    """ Return dict of transcript2data

    Args:
        gene_name (str): Gene to get transcript
        verbose (bool, optional): Verbose mode. Defaults to True.
        nirvana_data_dict (dict, optional): Dict if get_nirvana_data_dict has been run. Defaults to None.

    Returns:
        dict: Dict of transcript2transcript_data
    """

    hgnc_dict = {}
    gene_name = gene_name.upper()

    if not nirvana_data_dict:
        nirvana_data_dict = get_nirvana_data_dict()

    if gene_name not in hgnc_dict:
        nirvana_transcripts = nirvana_data_dict.get(gene_name, None)

        if nirvana_transcripts is None:
            new_gene = hgnc_queries.get_hgnc_symbol(gene_name)

            if new_gene:
                nirvana_transcripts = nirvana_data_dict.get(new_gene[0], None)

                if nirvana_transcripts:
                    hgnc_dict[gene_name] = new_gene
                else:
                    hgnc_dict[gene_name] = ""
            else:
                hgnc_dict[gene_name] = ""
    else:
        nirvana_transcripts = nirvana_data_dict.get(hgnc_dict[gene_name], None)

    if verbose:
        for transcript, transcript_data in nirvana_transcripts.items():
            print("\t".join([
                gene_name, transcript, transcript_data["chrom"],
                transcript_data["start"], transcript_data["end"],
                transcript_data["canonical"]
            ]))

    return nirvana_transcripts


def find_dnanexus_g2t():
    """ Return project and file id of the most recent g2t

    Returns:
        tuple: Project id and file id of latest g2t
    """

    data_objects = dxpy.find_data_objects(
        name="nirvana_genes2transcripts*",
        name_mode="glob",
        project="project-Fkb6Gkj433GVVvj73J7x8KbV"
    )

    most_recent_date = 0
    saved_id = None
    saved_project = None

    for data in list(data_objects):
        current_project = data["project"]
        current_file_id = data["id"]

        g2t_file = dxpy.DXFile(
            dxid=current_file_id, project=current_project)
        creation_date = g2t_file.describe(fields=("created",))["created"]

        # Using timestamp to get most recent g2t file
        if creation_date > most_recent_date:
            most_recent_date = creation_date
            saved_id = current_file_id
            saved_project = current_project

    return saved_project, saved_id


def get_already_assigned_transcripts(project: str, file_id: str):
    """ Return dict of g2t

    Args:
        project (str): Project id
        file_id (str): File id

    Returns:
        dict: Dict of g2t
    """

    g2t = {}

    with dxpy.DXFile(dxid=file_id, project=project) as f:
        for line in f:
            gene, transcript = line.strip().split()
            g2t[gene] = transcript

    return g2t
