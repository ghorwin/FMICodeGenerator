# FMICodeGenerator webpage

Sources of the webpage published via GitHub Pages from the `/docs` directory of this repository.

- Pages: `*.adoc` (AsciiDoc, rendered with [Asciidoctor](https://asciidoctor.org)); files starting with `_` are includes, not pages
- `_settings.adoc`: common attributes, included directly below the title of every page
- `docinfo-header.html`: navigation bar inserted at the top of every page
- `css/fmicodegen.css`: site stylesheet (imports `roboto_ubuntu.css` and `asciidoctor.css` from the MasterSim manual)
- `fonts/`, `images/`, `data/`: static assets, copied as-is

## Publishing

    ./publish.sh

generates the html files and replaces the content of `<repo>/docs`. Commit and push `docs` afterwards.
GitHub repository settings: *Pages* → *Deploy from a branch* → `master`, folder `/docs`.

## Adding a page

1. create `<name>.adoc` with a `= Title` line followed by `include::_settings.adoc[]`
2. link it with `xref:<name>.adoc[Text]` and, if needed, add it to `docinfo-header.html`
