#!/usr/bin/env python3
"""Fix divergent DOIs by finding correct ones through PubMed/CrossRef."""
import re, json, urllib.request, urllib.error, time, glob

ROOT = '/home/marceloclaro/opencode-ecosystem-core/livro-odontologia-ia'

# Known correct DOIs (manually verified)
CORRECTIONS = {
    # Sims-Williams 1987 - was 4806234, correct is 4806228
    "10.1038/sj.bdj.4806234": "10.1038/sj.bdj.4806228",
    # Krois 2019 periodontal bone loss - was correct already? Let's check
    "10.1038/s41598-019-44839-3": "10.1038/s41598-019-44839-3",  # Already correct!
}

def pubmed_search(term):
    """Search PubMed and return PMIDs."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(term)}&retmax=3&retmode=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("esearchresult", {}).get("idlist", [])
    except:
        return []

def pubmed_fetch(pmid):
    """Fetch PubMed entry and extract DOI."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read().decode()
            doi_m = re.search(r'<ArticleId IdType="doi">([^<]+)</ArticleId>', content)
            if doi_m:
                return doi_m.group(1)
            title_m = re.search(r'<ArticleTitle>([^<]+)</ArticleTitle>', content)
            title = title_m.group(1) if title_m else "Unknown"
            return f"NO DOI: {title[:80]}"
    except:
        return "FETCH ERROR"

def try_nearby_dois(base_doi, count=20):
    """Try nearby DOIs by varying the last digits."""
    import urllib.parse
    results = []
    base = base_doi.rsplit('.', 1)
    if len(base) != 2:
        return results
    prefix, suffix = base[0], int(base[1]) if base[1].isdigit() else 0
    if suffix == 0:
        return results
    
    for delta in range(-count, count+1):
        if delta == 0:
            continue
        test_suffix = suffix + delta
        if test_suffix < 0:
            continue
        test_doi = f"{prefix}.{test_suffix}"
        url = f"https://doi.org/{test_doi}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((test_doi, resp.getcode(), resp.url))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                results.append((test_doi, e.code, ""))
        except:
            pass
    
    return results

# Read the current pendentes.bib
with open(f'{ROOT}/referencias/dois-pendentes.bib', 'r') as f:
    content = f.read()

# For each divergent DOI, check nearby DOIs
divergent_dois = [
    "10.1038/sj.bdj.4806234",  # Found: 4806228
    "10.1016/j.oraloncology.2024.106789",  # Need to find
    "10.1016/j.oraloncology.2024.106812",  # Need to find
    "10.1002/hed.27890",  # Need to find
    "10.1002/hed.27912",  # Need to find
    "10.1016/j.ajodo.2024.01.015",  # Need to find
    "10.1016/j.cmpb.2024.108234",  # Need to find
    "10.1016/j.prosdent.2024.03.034",  # Need to find
    "10.1016/j.jcms.2023.09.005",  # Need to find
    "10.1038/s41586-023-06555-x",  # Need to find
    "10.1109/access.2024.3401234",  # Need to find
    "10.1111/prd.12567",  # Need to find
    "10.1111/jcpe.13890",  # Need to find
    "10.1016/j.compmedimag.2024.102347",  # Already fixed? Was replaced
    "10.1016/j.media.2024.103158",  # Need to find
    "10.1259/dmfr.20200425",  # Need to find
    "10.1111/ocr.12745",  # Need to find
    "10.1016/j.adaj.2023.06.002",  # Need to find
    "10.1111/jcpe.14012",  # Need to find
    "10.1111/cid.13390",  # Need to find
    "10.11607/jomi.10456",  # 404 - needs complete replacement
    "10.1016/j.ajodo.2024.03.008",  # Need to find
    "10.1016/j.ejwf.2023.12.002",  # Need to find
    "10.1179/bjo.23.1.1",  # Need to find
    "10.1038/s41591-021-01614-0",  # Need to find
    "10.1016/j.jdent.2021.103830",  # Need to find
    "10.1016/j.jebdp.2024.102058",  # Need to find
]

print("Checking nearby DOIs for each divergent entry...\n")
for doi in divergent_dois:
    print(f"\n{doi}:")
    results = try_nearby_dois(doi, 15)
    if results:
        for test_doi, code, url in results[:5]:
            print(f"  {test_doi} → HTTP {code}")
    else:
        print("  (no numerical suffix to vary)")
    time.sleep(0.3)
