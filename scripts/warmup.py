"""Pre-download safety models so the first demo call isn't slow.

Usage:
    uv run python scripts/warmup.py           # download + verify
    uv run python scripts/warmup.py --check   # just check cache
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

MODELS = [
    {
        "name": "PII detector",
        "repo": "iiiorg/piiranha-v1-detect-personal-information",
        "classes": ("AutoTokenizer", "AutoModelForTokenClassification"),
        "size": "~110MB",
    },
    {
        "name": "Toxicity classifier",
        "repo": "s-nlp/roberta_toxicity_classifier",
        "classes": ("AutoTokenizer", "AutoModelForSequenceClassification"),
        "size": "~125MB",
    },
]

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def is_cached(repo: str) -> bool:
    hf_cache = os.path.join(
        os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface")), "hub"
    )
    prefix = "models--" + repo.replace("/", "--")
    return any(d.startswith(prefix) for d in os.listdir(hf_cache)) if os.path.isdir(hf_cache) else False


def check() -> bool:
    all_ok = True
    for m in MODELS:
        if is_cached(m["repo"]):
            print(f"  {GREEN}✓{NC} {m['name']} cached")
        else:
            print(f"  {YELLOW}!{NC} {m['name']} not cached")
            all_ok = False

    # Check aceteam_aep importable
    try:
        import aceteam_aep
        version = getattr(aceteam_aep, "__version__", "installed")
        print(f"  {GREEN}✓{NC} aceteam-aep {version}")
    except ImportError:
        print(f"  {RED}✗{NC} aceteam-aep not importable")
        all_ok = False

    return all_ok


def download():
    import transformers

    for m in MODELS:
        if is_cached(m["repo"]):
            print(f"  {GREEN}✓{NC} {m['name']} already cached")
            continue

        print(f"  Downloading {m['name']} ({m['size']})...")
        tokenizer_cls = getattr(transformers, m["classes"][0])
        model_cls = getattr(transformers, m["classes"][1])
        tokenizer_cls.from_pretrained(m["repo"])
        model_cls.from_pretrained(m["repo"])
        print(f"  {GREEN}✓{NC} {m['name']} cached")


if __name__ == "__main__":
    check_only = "--check" in sys.argv

    if check_only:
        ok = check()
        sys.exit(0 if ok else 1)
    else:
        download()
        print(f"\n  {GREEN}Models ready.{NC}")
