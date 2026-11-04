const assert=require('node:assert/strict');
const fs=require('node:fs');
const X=require('./vendor/xlsx.full.min.js');
const E=require('./estimates.js');
const P=require('./planner.js');
const w=X.read(fs.readFileSync(require('node:path').join(__dirname,'../Data/Eateries and Uni locations.xlsx')));
const rows=n=>X.utils.sheet_to_json(w.Sheets[n],{header:1,defval:null,blankrows:true});
const model=E.create(rows('Classrooms'),rows('Restaurants'));
assert.equal(model.classrooms.length,8);assert.equal(model.restaurants.length,13);
assert.equal(model.travel.length,105);
const data=P.parse(model.travel,model.waits);
for(const c of data.locations)for(const d of data.locations){const r=P.rank(c,d,'12:00',data);assert.equal(r.results.length,13);assert.equal(r.unavailable.length,0);assert.equal(r.results.find(x=>x.name==='Vending Machine Area').wait,0);for(let i=1;i<r.results.length;i++)assert.ok(r.results[i].total>=r.results[i-1].total);}
assert.equal(P.rank(data.locations[0],data.locations[1],'19:00',data).results.length,0);
assert.throws(()=>P.parse(model.travel,[model.waits[0],['Bad',-1,1,1,1]]));
console.log('Verified 8 locations, 13 eateries, 104 pairs and all 64 start/destination combinations.');
