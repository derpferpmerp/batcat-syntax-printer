import json
import re
import subprocess
from xml.dom.minidom import parseString
import dicttoxml
import pandas
import yaml


def cmdout(cmd):
    decodedbytestring = re.findall(
        "(?<=b')(.*)(?=')",
        str(subprocess.check_output(f"{cmd}", shell=True)),
    )[0]
    decoded_escape_characters = re.sub("\\\\n", "\n", decodedbytestring)
    decoded_to_list = [x.split(":") for x in decoded_escape_characters.split("\n")]
    dctout = {}
    for syntaxes in decoded_to_list:
        if len(syntaxes) != 2:
            continue
        langs = syntaxes[1].split(",")
        dctout[syntaxes[0]] = langs
    return dctout


def runcmd(cmd):
    subprocess.call(cmd, shell=True)


def json2csv(jsn, prefix=None):
    prefix = f"{prefix}/" if prefix != None else ""
    with open("temp.json", "x+") as tempfile:
        jsonout = jsn
        keys = [v for v in jsonout.values()]
        maxrows = max(len(v) for v in keys)
        jsonout2 = {}
        actualkeys = [kk for kk in jsonout.keys()]

        for ind in range(len(keys)):
            value = keys[ind]
            while len(value) < maxrows:
                value.append("")
            jsonout2[actualkeys[ind]] = value

        cont2write = json.dumps(
            jsonout2,
            sort_keys=True,
            indent=4,
        )
        tempfile.write(cont2write)
    readjson = pandas.read_json("temp.json")
    csvdata = readjson.to_csv("temp.csv", index=None, header=True)
    with open("temp.csv") as tmpcsv:
        out = tmpcsv.read()
    runcmd("rm -rf temp.csv")
    runcmd("rm -rf temp.json")
    return out


def json2toml(jsn):
    keys = [key for key in jsn.keys()]
    keysfixed = []
    for unfixed in keys:
        keysfixed.append(unfixed.replace("#", "s").replace(" ", "-").replace("+", "p"))
    keys = keysfixed
    values = [value for value in jsn.values()]
    out_top = "[[metadata.extensions]]\n"
    for key in range(len(keys)):
        out_top += f"{keys[key]} = {values[key]}\n"
    return out_top


def json2xml(jsn, prefix=None):
    prefix = f"{prefix}/" if prefix != None else ""
    with open("temp.json", "x+") as tempfile:
        jsonout = jsn
        keys = [v for v in jsonout.values()]
        max(len(v) for v in keys)
        jsonout2 = {}
        actualkeys = [kk for kk in jsonout.keys()]

        for ind in range(len(keys)):
            value = keys[ind]
            jsonout2[actualkeys[ind]] = value

        cont2write = json.dumps(
            jsonout2,
            sort_keys=True,
            indent=4,
        )

        xml = dicttoxml.dicttoxml(json.loads(cont2write))
        dom = parseString(xml)
    return dom.toprettyxml()


def mkdirwithfiles(
    name,
    comp=False,
    yml=False,
    jsn=False,
    tml=False,
    useSF=False,
    csv=False,
    xml=False,
    allcomps=False,
):
    if allcomps:
        yml, jsn, tml, csv, comp, xml = [True, True, True, True, True, True]

    COMPRESSABLES = ["tar", "tar.gz", "tar.xz", "zip"]

    runcmd(f"rm -rf {name};mkdir {name}")
    if yml != False:
        ymlout = yaml.safe_dump(
            cmdout("batcat --list-languages"),
            default_flow_style=False,
        )
        with open(f"{name}/ymlout.yml", "x+") as ymlfile:
            ymlfile.write(ymlout)
        print("[DEV] Added YAML File")
    if jsn != False or tml != False:
        jsonout = json.dumps(
            cmdout("batcat --list-languages"),
            sort_keys=True,
            indent=4,
        )
        with open(f"{name}/jsonout.json", "x+") as jsonfile:
            jsonfile.write(jsonout)

        if tml != False:
            with open(f"{name}/tomlout.toml", "x+") as tomlfile:
                tomlfile.write(json2toml(cmdout("batcat --list-languages")))
            print("[DEV] Added TOML File")

        if csv != False:
            with open(f"{name}/csvout.csv", "x+") as csvfile:
                csvfile.write(json2csv(cmdout("batcat --list-languages"), prefix=name))
            print("[DEV] Added CSV File")

        if xml != False:
            with open(f"{name}/xmlout.xml", "x+") as xmlout:
                xmlout.write(json2xml(cmdout("batcat --list-languages"), prefix=name))
            print("[DEV] Added XML File")

        if jsn == False:
            runcmd(f"rm -rf {name}/jsonout.json")
        else:
            print("[DEV] Added JSON File")
    if not comp:
        return None
    elif comp in COMPRESSABLES:
        if "tar" in comp:
            runcmd(f"tar -cvf syntaxes.{comp} {name}/")
        elif comp == "zip":
            runcmd(f"zip –r syntaxes.zip {name}")
        runcmd(f"rm -rf {name}")
        if useSF:
            runcmd("sf -z syntaxes* | yh")
    else:
        return "[DEV] Invalid Compression Type"


mkdirwithfiles(
    "OUT-DIR",
    comp="tar.xz",
    yml=True,
    jsn=True,
    useSF=True,
    tml=True,
    csv=True,
    xml=True,
)
