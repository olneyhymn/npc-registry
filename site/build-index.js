const fs = require('fs').promises;

async function loadSearchJson() {
  const fileContent = await fs.readFile('public/search.json', 'utf8');
  const data = JSON.parse(fileContent);
  return data;
}

const lunrjs = require('lunr');

function makeIndex(posts) {
  return lunrjs(function () {
    this.ref('title');
    this.pipeline.add(lunrjs.stemmer);
    this.field('title');
    this.field('ministers');
    this.field('content');
    this.field('location');
    this.field('names');
    this.field('raw_data');
    posts.forEach(p => {
      this.add(p);
    });
  });
}

async function run() {
  const posts = await loadSearchJson();
  const index = makeIndex(posts);
  console.log(JSON.stringify(index));
}

run()
  .then(() => process.exit(0))
  .catch(error => {
    console.error(error.stack);
    process.exit(1);
  });
