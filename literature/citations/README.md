# Citation library: 03-fx-data-artefact

- Built 2026-10-17 by `_tools/depth-kit/citations.py` from every DOI / arXiv id found in the paper folder's notes, tables and reading notes (not raw data).
- DOIs found: 54. Resolved to a BibTeX/RIS entry (de-duplicated by title+year): 54. Entries without a DOI added from a hand list (metadata copied from the paper folder's own prior-work notes; each has a `note` field): 10. Unresolved DOIs: 0 (see `unresolved.csv`).
- Metadata comes from doi.org content negotiation (CSL JSON) and is converted without editing; no field is invented.

Import into Zotero: File > Import > choose `references.bib` (or `references.ris`), keep "Place imported collections and items into new collection".
Check the entries flagged in `unresolved.csv` by hand before citing them.
