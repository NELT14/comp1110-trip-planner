const survey=document.getElementById('survey-form');
function setupSurvey(data){
 for(const id of ['survey-start','survey-end'])for(const name of data.locations)document.getElementById(id).add(new Option(name,name));
 for(const name of data.restaurants.keys())document.getElementById('survey-restaurant').add(new Option(name,name));
 document.getElementById('survey-download').disabled=false;
}
survey.addEventListener('submit',event=>{
 event.preventDefault();if(!survey.reportValidity())return;
 const values=Object.fromEntries(new FormData(survey));
 const validLocation=v=>data.locations.includes(v);
 if(!validLocation(values.start)||!validLocation(values.destination)||!data.restaurants.has(values.restaurant))return;
 for(const field of ['wait_minutes','outbound_minutes','onward_minutes'])if(!Number.isFinite(Number(values[field]))||Number(values[field])<0||Number(values[field])>240)return;
 const header=['start','restaurant','destination','visit_date','restaurant_arrival','wait_minutes','outbound_minutes','onward_minutes'];
 const csv=header.join(',')+'\r\n'+header.map(k=>'"'+String(values[k]).replace(/"/g,'""')+'"').join(',')+'\r\n';
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='lunch-trip-response.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 document.getElementById('survey-status').textContent='Response file downloaded. Nothing was submitted or saved online. You can share the CSV with your project team.';
});
survey.addEventListener('input',()=>document.getElementById('survey-status').textContent='');
