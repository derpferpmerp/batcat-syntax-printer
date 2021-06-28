# batcat-syntax-printer
Tool That Creates an Archive with Batcat langs (toml, yaml, json, csv, and xml)

The tool is currently set up to create a tar.xz archive, which can be extracted by running `tar -xvf syntaxes.tar.xz`<br>
so, it can pretty much take all the languages (Gathered from executing `batcat --list-languages`, parse that into multiple<br>
different languages, create an archive, and return it back to you.

In order to install:<br>
```assembly
poetry install
poetry shell
python main.py
```

## File Output Examples:<br>

```xml
<XML>

<?xml version="1.0" ?>
<root>
  <key name="Assembly (x86_64)" type="list">
    <item type="str">yasm</item>
    <item type="str">nasm</item>
    <item type="str">asm</item>
    <item type="str">inc</item>
    <item type="str">mac</item>
  </key>
</root>
```

csv: (too complicated)<br>

```toml
[[TOML]]


[[metadata.extensions]]
ActionScript = ['as']
Advanced-CSV = ['csv', 'tsv']
AppleScript = ['applescript', 'script editor']
ARM-Assembly = ['s', 'S']
```
```json
json


{
  "ARM Assembly": [
    "s",
    "S"
  ],
  "ASP": [
    "asa"
  ],
  "AWK": [
    "awk"
  ],
  "ActionScript": [
    "as"
  ]
}
```


```yaml
YAML:


ARM Assembly:
- s
- S
ASP:
- asa
AWK:
- awk
ActionScript:
- as
Advanced CSV:
- csv
- tsv
AppleScript:
- applescript
- script editor
```










