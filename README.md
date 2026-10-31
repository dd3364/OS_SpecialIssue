# OS Special Issue: AI vs Human Referee Reports

Materials for the Organization Science proposal comparing AI-written referee reports with the human referee reports on the same papers.

## Documents

- [`docs/Technical_Appendix_AI_vs_Human_Reviews_v3.pdf`](docs/Technical_Appendix_AI_vs_Human_Reviews_v3.pdf): how we produce the AI reports, how we measure AI and human reports, and how we compare them. Includes the key terms and all prompts.
- [`docs/Pilot_Analysis_Summary.pdf`](docs/Pilot_Analysis_Summary.pdf): results of the pilot run on 10 published papers.

## Pilot data (`pilot/`)

| Path | What it is |
| --- | --- |
| `coding/p01_*.py` … `p10_*.py` | One file per paper. Each holds the paper's issue record (documented issues, who raised them, how the authors responded, and whether the published paper changed), the coded critique points of every human referee and of the AI report, the matches between critique points and documented issues, and the fact-check results. |
| `analyze.py` | Reads the coding files and computes every result in the summary, including the full and length-matched comparisons and the resampled intervals. |
| `make_figures.py` | Draws the five figures in the summary from the results files. |
| `results/results.json` | All summary results. |
| `results/per_paper.csv` | One row per paper. |
| `results/per_report.csv` | One row per report (each human referee and the AI). |
| `figures/` | The figures used in the summary. |

To reproduce the results and figures (Python 3, `matplotlib` for the figures):

```
cd pilot
python3 analyze.py
python3 make_figures.py
```

### Coding file format

Each coding file defines a dictionary `P`:

- `issues`: the issue record. Each issue has a description `d`, the referees who raised it in `by` (`ED` = editor; empty = unasked change), the authors' response `resp`, the revision type `rev` (substantive, presentation or none), and `emph=True` for emphasized issues.
- `human`: for each referee, a list of critique points as `(id, target, criticality, specificity, constructiveness, tone, same-match issues, related-match issues)`.
- `ai`: the AI report's critique points in report order, in the same format plus a short label.
- `factcheck`: number of AI statements checked and number of factual errors found.

The source papers, preprints and peer review files are not included. They are available from the journals' websites.
