# decspeak

A command-line tool for extracting English words (or their suffixes) that can be mapped entirely to digits using a customizable leet/dec-speak substitution map. Supports suffixes i.e. suffixes of words that can be spelled in such a manner, useful for cheap [1.111B xyz domains](https://gen.xyz/1111b) (e.g. `ass.355317.xyz` : ASSESSED :: `succ.355317.xyz` : SUCCESSED). Can be extended to support more general mappings by messing with the regex and altering the map sanity check. 

## Features

- **Full-word mapping**: Find words that translate completely into digits.  
- **Suffix mode**: Extract numeric representations of word suffixes within specified length bounds.  
- **Custom substitution map**: Override defaults via a YAML file.  
- **Parallel processing**: Utilizes all CPU cores by default for fast word list scanning.  
- **Flexible I/O**: Read word lists from local files or HTTP(S) URLs; output to YAML.

## Installation

```bash
git clone https://github.com/avi-amalanshu/decspeak.git
cd decspeak
```

> **Requirements**: Python 3.6+, `PyYAML`, `requests`

## Usage

```bash
python words.py --input <url> [OTHER OPTIONS]
```

### Options

```bash
  -i, --input URL_OR_PATH      Path or HTTP(S) URL of a newline-separated word list  [required]
  --mode {word,suffix}         “word” for full-word mapping; “suffix” for suffix extraction  [default: word]
  --minlen MIN                 Minimum length of numeric string to include         [default: 6]
  --maxlen MAX                 Maximum length of numeric string to include         [default: 9]
  -w, --workers N              Number of parallel workers (defaults to CPU count)
  -o, --output FILE            Output YAML filename

  -v, --verbose                Print results to console as well as file
  --subs_file PATH             Path to custom substitution map in YAML format
```

### Example: Full-word Mapping

```bash
python words.py \
  -i /path/to/wordlist.txt \
  --mode word \
  --minlen 4 \
  --maxlen 8 \
  -o words_leet.yaml \
  -v
```

### Example: Suffix Extraction from URL

```bash
python words.py \
  -i https://example.com/words.txt \
  --mode suffix \
  --minlen 6 \
  --maxlen 9 \
  --subs_file my_subs.yaml
```

## Custom Substitution Map

Create a YAML file (`my_subs.yaml`) defining your own character→digit mappings:

```yaml
# my_subs.yaml
o: "0"
s: "5"
a: "4"
e: "3"
i: "1"
b: "8"
d: "17"
r: "12"
```

Pass it via `--subs_file my_subs.yaml`. Keys must be single lowercase letters; values are digit strings.

## Output Format

The tool produces a YAML mapping from each numeric string to a list of original words:

```yaml
"355317":
  - assessed
"1337":
  - leet
```
