import argparse
import gzip
import json
import os
import subprocess
import sys

import pandas as pd
import requests

sys.path.append("/mnt/storage/home/kimy/projects/HGNC_api/bin")

import hgnc_queries


HGNC_DICT = {}


def get_nirvana_data_dict():
    nirvana_gff = "/mnt/storage/home/kimy/projects/panelapp/nirvana/Cache/26/GRCh37/GRCh37_RefSeq_26.gff.gz"
    nirvana_tx_dict = {}

    with gzip.open(nirvana_gff) as nir_fh:
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
                    gff_gene_name = value.replace('"','').upper()
                elif key == "transcript_id" and value.startswith('"NM_'):
                    gff_transcript = value.replace('"','')
                elif key == "tag":
                    gff_tag = value.replace('"','')

            if gff_gene_name and gff_transcript:
                chrom = fields[0].replace("chr", "")
                start, end = fields[3:5]
                canonical = gff_tag
                nirvana_tx_dict.setdefault(gff_gene_name, {})[gff_transcript] = {
                    "chrom":chrom,
                    "start":start,
                    "end":end,
                    "canonical":canonical
                }

    return nirvana_tx_dict


def nirvana_transcripts(gene_name, verbose=True, nirvana_data_dict=None):
    gene_name = gene_name.upper()
    
    if not nirvana_data_dict:
        nirvana_data_dict = get_nirvana_data_dict()

    if gene_name not in HGNC_DICT:
        nirvana_transcripts = nirvana_data_dict.get(gene_name, None)

        if nirvana_transcripts is None:
            new_gene = hgnc_queries.get_hgnc_symbol(gene_name)
            
            if new_gene:
                nirvana_transcripts = nirvana_data_dict.get(new_gene[0], None)
                
                if nirvana_transcripts:
                    HGNC_DICT[gene_name] = new_gene
                else:
                    HGNC_DICT[gene_name] = ""
            else:
                HGNC_DICT[gene_name] = ""
    else:
        nirvana_transcripts = nirvana_data_dict.get(HGNC_DICT[gene_name], None)

        
    if verbose:
        for transcript, transcript_data in nirvana_transcripts.items():
            print("\t".join([gene_name, transcript, transcript_data["chrom"], transcript_data["start"], transcript_data["end"], transcript_data["canonical"]]))

    return nirvana_transcripts


def get_panel_genes(panel_id, all_genes=False, version=None):
    """ Get the genes from a panel id 
    
    Confidence level 3 is the green genes from PanelApp
    """

    parameters = []
    genes = []

    prefix_url = "panels/{}/genes/".format(panel_id)

    if not all_genes:
        parameters.append("confidence_level=3")
    if version:
        parameters.append("version={}".format(version))

    if parameters:
        suffix_url = "&".join(parameters)
        ext_url = "{}?{}".format(prefix_url, suffix_url)
    else:
        ext_url = prefix_url

    panel = get_panelapp_response(ext_url = ext_url)

    res = get_full_results_from_stupid_PanelApp_system(panel)

    for data in res:
        genes.append(data["gene_data"]["hgnc_symbol"])
    
    return genes


def get_signedoff_panels_data():
    """ Get the panels IDs and versions of the signedoff panels

    The API doesn't allow much with the signedoff panels
    So need to get the version to use the manipulate the panel
    """

    panels = {}

    signedoff_panels = get_panelapp_response(ext_url="panels/signedoff")
    res = get_full_results_from_stupid_PanelApp_system(signedoff_panels)

    for data in res:
        panels[data["name"]] = {
            "id": data["id"],
            "version": data["version"],
            "disease_group": data["disease_group"],
            "disease_sub_group": data["disease_sub_group"]
        }
    
    return panels


def get_already_assigned_transcripts():
    nirvana_g2t = "/mnt/storage/data/NGS/nirvana_genes2transcripts"
    g2t = {}

    with open(nirvana_g2t) as f:
        for line in f:
            gene, transcript = line.strip().split()
            g2t[gene] = transcript

    return g2t


def get_transcripts_for_panels(panel_genes, nirvana_g2t, nirvana_data_dict):
    g2t = {}

    for gene in panel_genes:
        if gene in nirvana_g2t:
            selected_transcript = nirvana_g2t[gene]
            g2t[gene] = selected_transcript
        else:
            transcripts = nirvana_transcripts(gene, False, nirvana_data_dict)

            if transcripts:
                for transcript, field in transcripts.items():
                    if field["canonical"]:
                        selected_transcript = transcript
                        g2t[gene] = selected_transcript
            else:
                print("Gene \"{}\" not found in Nirvana GFF".format(gene))
                g2t[gene] = ""

    return g2t


def write_panels(panels, panel_folder):
    signedoff_panels = {}
    nirvana_g2t = get_already_assigned_transcripts()
    nirvana_data_dict = get_nirvana_data_dict()

    for panel_name, panel_data in panels.items():
        panel_id = panel_data["id"]
        version = panel_data["version"]

        panel_genes = get_panel_genes(panel_id, version=version)
        g2t = get_transcripts_for_panels(panel_genes, nirvana_g2t, nirvana_data_dict)

        signedoff_panels[panel_name] = {
            "id": panel_id,
            "version": version,
            "g2t": g2t,
        }

    if not os.path.isdir(panel_folder):
        os.mkdir(panel_folder)

    for panel, fields in signedoff_panels.items():
        file_name = "/mnt/storage/home/kimy/projects/panelapp/{}/{}_{}".format(
            panel_folder,
            "_".join([ele for ele in panel.replace("-", " ").split()]),
            signedoff_panels[panel]["version"]
        )

        with open(file_name, "w") as f:
            for gene, transcript in signedoff_panels[panel]["g2t"].items():
                f.write("{}\t{}\n".format(gene, transcript))
        
        print("File {} written".format(file_name))


def write_group_diseases(panels, output_path):
    disease_groups = {}
    signedoff_panels = {}

    for panel_name, panel_data in panels.items():
        disease_group = panel_data["disease_group"]
        disease_sub_group = panel_data["disease_sub_group"]
        
        if not disease_group:
            disease_group = "No group"

        signedoff_panels[panel_name] = {
            "disease_group": disease_group,
            "disease_sub_group": disease_sub_group
        }

        disease_groups.setdefault(disease_group, []).append(panel_name)

    d = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in disease_groups.items()]))

    d.to_csv(
        output_path,
        index=False,
        sep="\t"
    )

    print("{} was written".format(output_path))


def get_full_results_from_stupid_PanelApp_system(data):
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


def get_panelapp_response(ext_url = None, full_url = None):
    """ Get response from swagger panelapp api """

    if full_url:
        url = full_url
    else:
        url = "https://panelapp.genomicsengland.co.uk/api/v1/{}".format(ext_url)

    try:
        request = requests.get(url, headers = {"Accept": "application/json"})
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


def get_latest_version_of_panel(panel_id):
    panel_data = get_panelapp_response(ext_url="panels/{}".format(panel_id))
    return panel_data["version"]


def compare_panel_versions(panel_id, all_genes, version1, version2=None):
    panel_version1 = get_panel_genes(panel_id, all_genes, version1)
    panel_version2 = get_panel_genes(panel_id, all_genes, version2)

    in_version1 = []
    in_version2 = []

    if not version2:
        version2 = "{} (latest)".format(get_latest_version_of_panel(panel_id))

    for gene in panel_version1:
        if gene not in panel_version2:
            in_version1.append(gene)
    
    for gene in panel_version2:
        if gene not in panel_version1:
            in_version2.append(gene)

    if in_version1:
        print("The following genes are present in {}:".format(version1))
        
        for gene in in_version1:
            print(gene)

    if in_version2:
        print("The following genes are present in {}:".format(version2))

        for gene in in_version2:
            print(gene)

    print("There are {} genes in panel {} version {}".format(len(panel_version1), panel_id, version1))
    print("There are {} genes in panel {} version {}".format(len(panel_version2), panel_id, version2))


def main(parser, **sub_args):
    if parser == "panel":
        if sub_args["compare"]:
            compare_panel_versions(
                sub_args["identifier"],
                sub_args["all"],
                sub_args["version"]
            )

        if sub_args["genes"]:
            genes = get_panel_genes(
                sub_args["identifier"],
                sub_args["all"],
                sub_args["version"]
            )
            for gene in genes:
                print(gene)

    elif parser == "signedoff":
        panels = get_signedoff_panels_data()

        if sub_args["write"] != False:
            write_panels(panels, sub_args["write"])
        
        if sub_args["disease"] != False:
            write_group_diseases(panels, sub_args["disease"])



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Panelapp script")
    subparser = parser.add_subparsers(dest="subparser")
    
    signedoff_parser = subparser.add_parser("signedoff", help="Get signedoff panels")
    signedoff_parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Get all genes not just green genes"
    )
    signedoff_parser.add_argument(
        "-w",
        "--write",
        const="panels",
        nargs="?",
        default=False,
        help="Write panels in tsv Dias file: in panels/ folder, \{panelname\}_\{version\}"
    )
    signedoff_parser.add_argument(
        "-d",
        "--disease",
        const="disease_panels.tsv",
        nargs="?",
        default=False,
        help="Write signedoff panels in following format:\
            disease as header and panels underneath"
    )

    panel_parser = subparser.add_parser("panel", help="Panel operations")
    panel_parser.add_argument(
        "-i",
        "--identifier",
        help="Panel id, panel name doesn't work when using version for some reason"
    )
    panel_parser.add_argument(
        "-v", 
        "--version",
        help="Version of panel to get"
    )
    panel_parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Get all genes not just green genes"
    )
    panel_parser.add_argument(
        "-c",
        "--compare",
        action="store_true",
        default=False,
        help="Compare given version of a panel to the latest version"
    )
    panel_parser.add_argument(
        "-g",
        "--genes",
        action="store_true",
        default=False,
        help="Returns genes from panel id"
    )

    args = vars(parser.parse_args())
    type_op = args.pop("subparser")
    sub_args = args

    main(type_op, **sub_args)