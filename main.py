import json
import re
import subprocess
from xml.dom.minidom import parseString
import dicttoxml
import pandas
import yaml
from sty import ef, fg, rs


global languages
global FORMATS
global DMP
DMP = 0

print("")

FORMATS = [
	"YAML",
	"JSON",
	"XML",
	"INI",
	"CSV",
	"TOML",
]


def prDevMessage(msg, dmpin):
	fn = re.findall("[A-Z]+[A-Z]", msg)[0]
	if fn not in FORMATS:
		FORMATS.append(fn)
	maxlen = max(len(ln) for ln in FORMATS)
	MAXLENGTH = round(200 * max(len(f"[ DEV ] Added {fn} File") for ln in FORMATS))
	amtspaces = 0
	while len(fn) < maxlen:
		fn, amtspaces = [fn + " ", amtspaces + 1]

	amtspaces -= 4 + abs(MAXLENGTH-len(str(re.sub(" ", "", fn))))

	out = fg(152, 236, 231) + f"{fn}" + fg.rs + fg(0, 255, 0)
	out = ef.italic + out + "".join([" " for space in range(1,amtspaces)]) + rs.italic

	msg = msg.replace(str(re.sub(" ", "", fn)), out)

	devmsg = (
		fg.red
		+ "\u2588 "
		+ fg.rs
		+ fg(255, 255, 255)
		+ "[ "
		+ fg.rs
		+ fg(255, 0, 0)
		+ "DEV"
		+ fg.rs
		+ fg(255, 255, 255)
		+ " ]"
		+ fg.rs
		+ fg(0, 255, 0)
		+ f" {msg}"
		+ fg.rs
		+ fg.red
		+ " \u2588"
		+ fg.rs
	)
	print(f"\t{devmsg}")


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


# MAIN COMMAND
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
def el_in_a_equal_to_b(a, b, notb=False):
	if notb:
		return True if [itm for itm in a if itm != b] != [] else False
	else:
		return True if [itm for itm in a if itm == b] != [] else False


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


def setall(var, val):
	return [val for val in range(len(var))]


def mkdirwithfiles(
	name,
	comp=False,
	yml=False,
	jsn=False,
	tml=False,
	useSF=False,
	csv=False,
	xml=False,
	ini=False,
	allcomps=False,
):
	if allcomps:
		yml, jsn, tml, csv, comp, xml, ini = setall(
			[yml, jsn, tml, csv, comp, xml, ini], True
		)
		comp = "tar.xz"

	COMPRESSABLES = ["tar", "tar.gz", "tar.xz", "zip"]

	runcmd(f"rm -rf {name};mkdir {name}")
	maxamt = max(len(f"Added {ln} File") for ln in FORMATS) + 10
	strout = f"{fg.red}\u2588{fg.rs}"
	for bariter in range(maxamt):
		varout2 = f"{fg.red}\u2580{fg.rs}"
		strout += varout2
	print(f"\t{strout}{fg.red}\u2588{fg.rs}")
	strout = "\t" + strout.replace("\u2580", "\u2584") + fg.red + "\u2588" + fg.rs
	if yml != False:
		ymlout = yaml.safe_dump(
			languages,
			default_flow_style=False,
		)
		with open(f"{name}/ymlout.yml", "x+") as ymlfile:
			ymlfile.write(ymlout)
		prDevMessage("Added YAML File", DMP)

	if el_in_a_equal_to_b([jsn, tml, csv, xml, ini], False, notb=True):
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
			prDevMessage("Added TOML File", DMP)

		if csv != False:
			with open(f"{name}/csvout.csv", "x+") as csvfile:
				csvfile.write(json2csv(languages, prefix=name))
			prDevMessage("Added CSV File", DMP)

		if xml != False:
			with open(f"{name}/xmlout.xml", "x+") as xmlout:
				xmlout.write(json2xml(languages, prefix=name))
			prDevMessage("Added XML File", DMP)

		if ini != False:
			with open(f"{name}/iniout.ini", "x+") as iniout:
				iniout.write(json2ini(languages))
			prDevMessage("Added INI File", DMP)

		if jsn == False:
			runcmd(f"rm -rf {name}/jsonout.json")
		else:
			prDevMessage("Added JSON File", DMP)

	if not comp:
		prDevMessage("Completed (No Compression)")
	elif comp in COMPRESSABLES:
		print(strout)
		if "tar" in comp:
			runcmd(f"tar -cf syntaxes.{comp} {name}/")
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
	useSF=False,
	tml=True,
	csv=True,
	xml=True,
	ini=True,
)

runcmd("rm -rf temp*")
print("")