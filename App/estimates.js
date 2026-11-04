/* Provisional scenario assumptions, not measured venue performance. */
(function(root){
const waiting={
 'Union Restaurant':[7,20,8,12], 'CYM Canteen':[6,18,7,10],
 '27 Kebab House':[8,16,8,12], 'BIJAS Vegetarian':[8,18,8,12],
 'Alfafa bistro':[10,22,10,16], 'Starbucks':[4,10,5,6],
 'The Sandwich Club':[4,12,5,6], 'Subway':[5,14,6,8],
 'Hong Kong Daily':[7,18,8,12], 'TamJai Samgor':[10,24,10,18],
 'Asian Gourmet':[8,20,8,14], 'Urban Coffee Roaster':[5,12,5,7],
 'Vending Machine Area':[0,0,0,0]
};
const normalize=s=>String(s||'').trim().toLowerCase().replace(/[^a-z0-9]/g,'');
function records(rows){const header=rows.findIndex(r=>r[1]==="Area"&&r[2]==="Floor");if(header<0)throw Error("Location sheet headers are missing.");return rows.slice(header+1).filter(r=>typeof r[0]==='string'&&r[0].trim()).map(r=>({name:r[0].trim(),area:String(r[1]||'').trim(),floor:String(r[2]||'').trim(),building:String(r[3]||'').trim()}));}
function floor(s){if(s.includes(','))return 0;const m=/^(\d+)\/F$/i.exec(s);return m?Number(m[1]):s.toUpperCase()==='LG/F'?-1:0;}
function walking(a,b){
 const sameBuilding=normalize(a.building)&&normalize(a.building)===normalize(b.building);
 const area=x=>normalize(x.area)==='centennialcampus'?'centennial':'main';
 const base=sameBuilding?2:area(a)===area(b)?6:12;
 return base+Math.ceil(Math.abs(floor(a.floor)-floor(b.floor))*0.5);
}
function create(classroomRows,restaurantRows){
 const classrooms=records(classroomRows),restaurants=records(restaurantRows);
 const travel=[['Start location','Final location','walk distance (min)']];
 classrooms.forEach(c=>restaurants.forEach(r=>travel.push([c.name,r.name,walking(c,r)])));
 const waits=[['Restaurant name','09:00–12:00','12:00–14:00','14:00–17:00','17:00–19:00']];
 restaurants.forEach(r=>waits.push([r.name,...(/vending/i.test(r.name)?[0,0,0,0]:waiting[r.name]||[8,20,8,14])]));
 return {travel,waits,classrooms,restaurants};
}
root.Estimates={create,walking};if(typeof module!=='undefined')module.exports=root.Estimates;
})(globalThis);
