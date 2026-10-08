async function loadAdmin(){
 const r=await api('/api/admin/overview');
 if(!r.success){const s=document.getElementById('stats');if(s)s.innerHTML='<div class="empty">'+(r.error||'Unable to load admin data')+'</div>';return}
 const s=document.getElementById('stats');const d=document.getElementById('deps');
 if(s)s.innerHTML=Object.entries(r.stats||{}).map(([k,v])=>`<div class="stat"><span>${k.replaceAll('_',' ')}</span><b>${v}</b></div>`).join('');
 const deps=await api('/api/admin/departments');
 if(d)d.innerHTML=(deps.departments||[]).map(x=>`<div class="case-row"><div><b>${x.name}</b><span>${x.code}</span></div><strong>${x.is_active?'ACTIVE':'INACTIVE'}</strong></div>`).join('')||'<div class="empty">No departments.</div>';
}
document.addEventListener('DOMContentLoaded',loadAdmin);
