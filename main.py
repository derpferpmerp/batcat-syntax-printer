import json
import re
import subprocess
from xml.dom.minidom import parseString
import dicttoxml
import pandas
import yaml
from sty import fg


global languages

def prDevMessage(msg):
	devmsg = fg(255,255,255) + "[ " + fg.rs + fg(255,0,0) + "DEV" + fg.rs + fg(255,255,255) + " ]" + fg.rs + fg(0,255,0) + f" {msg}" + fg.rs
	print(devmsg)



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

languages = cmdout("batcat --list-languages")


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

def json2ini(jsn):
	keys = [key for key in jsn.keys()]
	keysfixed = []
	for unfixed in keys:
		keysfixed.append(unfixed.replace("#", "s").replace("+", "p"))
	keys = keysfixed
	values = [value for value in jsn.values()]
	out_top = "[metadata.extensions]\n"
	for key in range(len(keys)):
		out_top += f"{keys[key]} = {values[key]}\n"
	return out_top


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


# Returns True if there is an item in List "a" that is equal to value "b"
def el_in_a_equal_to_b(a,b,notb=False):
	if notb:
		return(True if [itm for itm in a if itm != b] != [] else False)
	else:
		return(True if [itm for itm in a if itm == b] != [] else False)


def json2xml(jsn, prefix=None):
	prefix = f"{prefix}/" if prefix != None else ""
	with open("temp.json", "x+") as tempfile:
		jsonout = jsn
		keys = [v for v in jsonout.values()]
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

def setall(var,val):
	return [val for val in range(len(var))]


def mkdirwithfiles(name,comp=False,yml=False,jsn=False,tml=False,useSF=False,csv=False,xml=False,ini=False,allcomps=False):
	if allcomps:
		yml, jsn, tml, csv, comp, xml, ini = setall([yml,jsn,tml,csv,comp,xml,ini],True)
		comp = "tar.xz"

	COMPRESSABLES = ["tar", "tar.gz", "tar.xz", "zip"]

	runcmd(f"rm -rf {name};mkdir {name}")
	if yml != False:
		ymlout = yaml.safe_dump(
			languages,
			default_flow_style=False,
		)
		with open(f"{name}/ymlout.yml", "x+") as ymlfile:
			ymlfile.write(ymlout)
		prDevMessage("Added YAML File")

	if el_in_a_equal_to_b([jsn,tml,csv,xml,ini],False,notb=True):
		jsonout = json.dumps(
			languages,
			sort_keys=True,
			indent=4,
		)
		with open(f"{name}/jsonout.json", "x+") as jsonfile:
			jsonfile.write(jsonout)

		if tml != False:
			with open(f"{name}/tomlout.toml", "x+") as tomlfile:
				tomlfile.write(json2toml(languages))
			prDevMessage("Added TOML File")

		if csv != False:
			with open(f"{name}/csvout.csv", "x+") as csvfile:
				csvfile.write(json2csv(languages, prefix=name))
			prDevMessage("Added CSV File")

		if xml != False:
			with open(f"{name}/xmlout.xml", "x+") as xmlout:
				xmlout.write(json2xml(languages, prefix=name))
			prDevMessage("Added XML File")

		if ini != False:
			with open(f"{name}/iniout.ini", "x+") as iniout:
				iniout.write(json2ini(languages))
			prDevMessage("Added INI File")

		if jsn == False:
			runcmd(f"rm -rf {name}/jsonout.json")
		else:
			prDevMessage("Added JSON File")

	if not comp:
		prDevMessage("Completed (No Compression)")
	elif comp in COMPRESSABLES:
		if "tar" in comp:
			runcmd(f"tar -cvf syntaxes.{comp} {name}/")
		elif comp == "zip":
			runcmd(f"zip –r syntaxes.zip {name}")
		runcmd(f"rm -rf {name}")
		if useSF:
			runcmd("sf -z syntaxes* | batcat -l yaml")
	else:
		prDevMessage("Invalid Compression Type")


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

runcmd("rm -rf temp*")
