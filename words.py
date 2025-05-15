import re
import yaml
import requests
from argparse import ArgumentParser
from multiprocessing import Pool, cpu_count

# -----------------------------------------------------------------------------
# default substitution map
# -----------------------------------------------------------------------------
subs = {
#    'for': '4', 
#    'four': '4',
#    'to':  '2',
#    'ate': '8', 
#    'ten': '10',
#    'g':   '6',
    'o':   '0', 
    's':   '5',
#    't':   '7', 
    'a':   '4', 
    'b':   '8',
    'e':   '3', 
    'i':   '1',
#    'm':  '44',
    'd':  '17',
#    'y':   '7',
    'r':  '12',
}

KEYS_BY_LEN = sorted(subs.keys(), key=len, reverse=True)
PATTERN = re.compile(
    "|".join(re.escape(k) for k in KEYS_BY_LEN)
)

def replace_string(s: str) -> str:
    return PATTERN.sub(lambda m: subs[m.group(0)], s)

# -----------------------------------------------------------------------------
# Argument parsing & word loading
# -----------------------------------------------------------------------------
def parse_args():
    p = ArgumentParser(
        description="Map English words (or their suffixes) to numeric substitutions"
    )
    p.add_argument("-i", "--input",   required=True,
                   help="URL (http://… or https://…) or path to a local .txt word list")
    p.add_argument("--mode", choices=("word","suffix"), default="word",
                   help="'word': full-word mapping; 'suffix': all numeric suffixes ≥ minlen")
    p.add_argument("--minlen", type=int, default=6,
                   help="minimum length of numeric string to include")
    p.add_argument("--maxlen", type=int, default=9,
                   help="maximum length of numeric string to include")
    p.add_argument("-w","--workers", type=int, default=cpu_count(),
                   help="number of parallel worker processes")
    p.add_argument("-o","--output",
                   help="output YAML filename (defaults to <mode>_<minlen>_<maxlen>.yaml)")
    p.add_argument("-v","--verbose", action="store_true",
                   help="verbose (prints output to console)")
    return p.parse_args()

def load_words(source):
    """
    Generator over one word per line, lower-cased.
    Supports HTTP(S) URLs or local file paths.
    """
    if source.startswith(("http://","https://")):
        resp = requests.get(source)
        resp.raise_for_status()
        for line in resp.text.splitlines():
            yield line.strip().lower()
    else:
        with open(source, "r") as f:
            for line in f:
                yield line.strip().lower()

# -----------------------------------------------------------------------------
# suffix-mode helper func: dp to find all fully-translatable suffixes
# -----------------------------------------------------------------------------
def find_suffixes(word: str, mn: int, mx: int):
    """
    return a set of all digit-strings r such that
      - r was produced by replacing every character of some suffix word[i:]
        via the subs-map
      - the entire suffix word[i:] is coverable by the subs-keys
      - len(r) is between mn and mx
    """
    N = len(word)
    # dp[i] means word[i:] is fully segmentable into subs-keys
    dp = [False]*(N+1)
    dp[N] = True

    # Build dp table backwards
    for i in range(N-1, -1, -1):
        for key in KEYS_BY_LEN:
            end = i + len(key)
            if end <= N and dp[end] and word.startswith(key, i):
                dp[i] = True
                break

    results = set()
    for i in range(N):
        if not dp[i]:
            continue
        suffix = word[i:]
        replaced = replace_string(suffix)
        # only digits? (since dp said it's fully covered, replace_string
        # will have turned it to digits, but verify with isdigit)
        if replaced.isdigit() and mn <= len(replaced) <= mx:
            results.add(replaced)
    return results

# -----------------------------------------------------------------------------
# worker
# -----------------------------------------------------------------------------
def process_word(args):
    """
    Worker: pure function, no side-effects.
    Returns a list of (key, original_word) pairs.
    """
    word, mode, mn, mx = args

    if mode == "word":
        replaced = replace_string(word)
        if replaced.isdigit() and mn <= len(replaced) <= mx:
            return [(replaced, word)]
        return []

    # suffix mode
    if len(word) < mn:
        return []
    suffixes = find_suffixes(word, mn, mx)
    return [(suf, word) for suf in suffixes]

# -----------------------------------------------------------------------------
# driver
# -----------------------------------------------------------------------------
def main():
    args = parse_args()

    with Pool(args.workers) as pool:
        tasks = (
            (w, args.mode, args.minlen, args.maxlen)
            for w in load_words(args.input)
        )
        all_results = pool.map(process_word, tasks)

    mapping = {}
    for sublist in all_results:
        for key, word in sublist:
            mapping.setdefault(key, []).append(word)

    out_name = args.output or f"{args.mode}_{args.minlen}_{args.maxlen}.yaml"
    with open(out_name, "w") as fout:
        yaml.dump(mapping, fout, sort_keys=True)

    if args.verbose:
        print(yaml.dump(mapping, sort_keys=True))

if __name__ == "__main__":
    main()

