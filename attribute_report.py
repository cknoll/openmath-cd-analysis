"""
This script evaluates the consistency of attributes of openmath content dictionaries (CDs).
It runs through all files a hardcoded directory and produces a list of those "symbols" (the entities
which are defined inside a CD) which see to have inkonsistent attributes w.r.t. to their
`<OMOBJ ...>` tag.
"""

import glob
import os

from bs4 import BeautifulSoup, NavigableString
from addict import Dict as attr_dict
from textwrap import dedent as twdd
import yaml  # pip install pyyaml

from ipydex import IPS, activate_ips_on_exception
activate_ips_on_exception()



def process_file(fpath):


    res = attr_dict()

    with open(fpath, "r") as xmlfile:
        xmldata = xmlfile.read()
        soup = BeautifulSoup(xmldata, 'lxml')

    cdnames = soup.find_all("cdname")
    assert len(cdnames) == 1

    res.cdname = cdnames[0].contents[0]
    res.description = soup.findChild("description").contents[0].strip()
    res.defined_items = []


    definitions = soup.find_all("cddefinition")

    for defn in definitions:
        def_res = attr_dict()
        def_res.fpath = fpath
        def_res.name = defn.findChild("name").contents[0]
        # def_res.description = defn.findChild("description").contents[0].strip()


        omobj_child = defn.findChild("omobj")
        if omobj_child:
            def_res.omobj_tag_present = True
            omobj_attrs = omobj_child.attrs
        else:
            def_res.omobj_tag_present = False
            # their is no omobj-tag: → empty dict
            omobj_attrs = dict()

        a1 = def_res.omobj_attr_cdbase = omobj_attrs.get("cdbase")
        a2 = def_res.omobj_attr_version = omobj_attrs.get("version")
        a3 = def_res.omobj_attr_xmlns = omobj_attrs.get("xmlns")

        def_res.some_attr_missing = None in (a1, a2, a3)


        def_res2 = dict([(key, value if isinstance(value, bool) else str(value)) for key, value in def_res.items()])
        res.defined_items.append(def_res2)

    return res




path = "../CDs/cd/Official"
# advantage over os.listdir: wildcard filtering
list_of_files = glob.glob(f"{path}/*.ocd")
list_of_files.sort()


list1 = []
list2 = []

for fpath in list_of_files:

    res = process_file(fpath)

    # note "items" here are "symbols" defined in the CDs
    for itm in res.defined_items:
        if itm["some_attr_missing"]:
            list1.append(itm)
        else:
            list2.append(itm)
        try:
            yaml.safe_dump(itm)
        except:
            IPS()
            raise


result = {"seemigliy_inconsistent_symbols": list1, "seemingly_consistent_symbols": list2}

target_fname = "results.yml"
with open(target_fname, "w") as ymlfile:
    yaml.safe_dump(result, ymlfile, allow_unicode=True)

print(f"{target_fname} written")




