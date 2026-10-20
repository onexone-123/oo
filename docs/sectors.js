const SectorTrends=(()=>{
 let data=null,region='china',category='all';
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const names={tech:'科技',entertainment:'娱乐',fashion:'时尚'};
 async function load(){try{const r=await fetch('sectors.json');if(!r.ok)throw Error();data=await r.json()}catch{data=null}}
 function render(query=''){
  const rows=(data?.items||[]).filter(x=>x.region===region&&(category==='all'||x.category===category)&&(!query||JSON.stringify(x).toLowerCase().includes(query.toLowerCase())));
  return `<div class="board-tabs"><button class="outline ${region==='china'?'selected':''}" data-sector-region="china">中国趋势</button><button class="outline ${region==='world'?'selected':''}" data-sector-region="world">全球趋势</button></div><div class="board-tabs">${[['all','全部'],...Object.entries(names)].map(([k,v])=>`<button class="outline ${category===k?'selected':''}" data-sector-category="${k}">${v}</button>`).join('')}</div><p class="footnote">编辑观察更新：${esc(data?.updated_at||'尚未载入')} · 全球栏目目前以英文公开材料为主，不代表所有国家。趋势是基于所列事件的判断，非全行业排名。</p><div class="sector-grid">${rows.map(x=>`<article class="sector-card"><span class="tag">${names[x.category]} / ${region==='china'?'中国':'全球'}</span><h2>${esc(x.title)}</h2><p class="sector-summary">${esc(x.summary)}</p><h3>具体看到了什么</h3><ul>${x.facts.map(t=>`<li>${esc(t)}</li>`).join('')}</ul><h3>背后的变化 <small>编辑判断</small></h3><p>${esc(x.logic)}</p><h3>哪些人更可能关注 <small>待验证</small></h3><p>${esc(x.audience)}</p><h3>可以怎样跟进</h3><p>${esc(x.action)}</p><div class="limits">${esc(x.boundary)}</div></article>`).join('')||'<p class="empty">暂无匹配内容，请重新载入或调整筛选。</p>'}</div>`;
 }
 function select(type,value){if(type==='region'&&['china','world'].includes(value))region=value;if(type==='category'&&['all',...Object.keys(names)].includes(value))category=value}
 return {load,render,select};
})();
