/* Calculation functions shared by the browser and tests. */
(function(root){
const key=(a,b)=>JSON.stringify([a,b].sort());
function duration(v){if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>=1440)throw Error('Times must be numeric minutes between 0 and 1440.');return v;}
function parse(travel,waits){
 if(JSON.stringify(travel[0])!==JSON.stringify(['Start location','Final location','walk distance (min)']))throw Error('Unexpected travel file headers.');
 if(waits[0]?.[0]!=='Restaurant name')throw Error('Unexpected restaurant file headers.');
 const bands=waits[0].slice(1).map(h=>{const m=/^(\d{2}):([0-5]\d)[–-](\d{2}):([0-5]\d)$/.exec(h);if(!m)throw Error('Invalid time interval: '+h);const lo=+m[1]*60 + +m[2], hi=+m[3]*60 + +m[4];if(lo>=hi||hi>1440)throw Error('Invalid time interval.');return {lo,hi,label:h};});
 bands.forEach((b,i)=>{if(i&&b.lo<bands[i-1].hi)throw Error('Time intervals overlap.');});
 const routes=new Map(), locations=new Set(),restaurants=new Map();
 for(const [a,b,t] of travel.slice(1)){if(!a||!b)throw Error('Missing location name.');const k=key(a,b);if(routes.has(k))throw Error('Duplicate travel pair.');routes.set(k,t==null?null:duration(t));locations.add(a);}
 for(const [name,...values] of waits.slice(1)){if(!name||restaurants.has(name))throw Error('Missing or duplicate restaurant name.');if(values.length!==bands.length)throw Error('Missing restaurant time columns.');restaurants.set(name,values.map(v=>v==null?null:duration(v)));}
 if(!locations.size||!restaurants.size||!bands.length)throw Error('The Excel files contain no usable data.');
 return {routes,locations:[...locations].sort(),restaurants,bands};
}
function rank(start,end,time,data){
 if(!data.locations.includes(start)||!data.locations.includes(end))throw Error('Choose valid locations.');
 if(!/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(time))throw Error('Enter a valid departure time.');
 const [h,m]=time.split(':').map(Number),results=[],unavailable=[];
 for(const [name,waits] of data.restaurants){const outbound=data.routes.get(key(start,name)),onward=data.routes.get(key(end,name));
 if(outbound==null||onward==null){unavailable.push({name,reason:'Walking time unavailable'});continue;}
 const arrival=h*60+m+outbound,i=data.bands.findIndex(b=>b.lo<=arrival&&arrival<b.hi);
 if(i<0||waits[i]==null){unavailable.push({name,reason:'No waiting estimate at restaurant arrival time'});continue;}
 results.push({name,outbound,onward,wait:waits[i],total:outbound+onward+waits[i],band:data.bands[i].label});}
 results.sort((a,b)=>a.total-b.total||a.name.localeCompare(b.name));results.forEach((r,i)=>r.rank=i&&results[i-1].total===r.total?results[i-1].rank:i+1);
 return {results,unavailable};
}
root.Planner={parse,rank};if(typeof module!=='undefined')module.exports=root.Planner;
})(globalThis);
