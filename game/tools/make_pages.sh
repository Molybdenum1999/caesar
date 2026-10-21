#!/bin/sh
# Rebuild docs/ (the GitHub Pages copy) from game/.
# The artifact host adds the <!doctype>/<head>/<body> skeleton itself, so game/index.html
# leaves it out; GitHub Pages serves files as-is, so the copy gets the skeleton here.
set -e
cd "$(dirname "$0")/../.."
rm -rf docs && mkdir -p docs
{
  printf '%s\n' '<!doctype html>' '<html lang="en">' '<head>' '<meta charset="utf-8">' \
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">' \
    '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>' '</head>' '<body>'
  cat game/index.html
  printf '%s\n' '</body>' '</html>'
} > docs/index.html
cp -r game/assets docs/assets
touch docs/.nojekyll
echo "docs/ rebuilt"
