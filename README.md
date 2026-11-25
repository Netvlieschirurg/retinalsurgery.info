# retinalsurgery.info

English version of [netvliesoperatie.info](https://netvliesoperatie.info), the patient-information site of Dr Koen van Overdam, vitreoretinal surgeon.

Do not edit the site here. Everything comes from the repository `Netvlieschirurg/netvliesoperatie.info`:

- `.github/workflows/mirror.yml` checks every 20 minutes for a new commit there, runs `mirror.py` and publishes the result with GitHub Pages.
- `mirror.py` copies `index.html`, `img/` and `fonts/`, makes English the default language, sends the NL button to netvliesoperatie.info, and puts the English title, description, canonical and hreflang links in the HTML.
- To update at once: Actions > "Engelse site bijwerken" > Run workflow.
