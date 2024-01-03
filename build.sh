#!/bin/bash
# fail if any commands fails
set -eux
pip install -r requirements.txt
mkdir -p site/content/churches
python extract2.py
cd site
npm install
node build-index.js >static/search_index.json
hugo --gc --minify -b ${DEPLOY_PRIME_URL}
