const Brandstar = (() => {
  let data = {items: []};
  let expanded = false, currentPage = '', currentQuery = '';
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const url = value => /^https:\/\/www\.brandstar\.com\.cn\/(in-depth|news)\/\d+$/.test(value) ? value : 'https://www.brandstar.com.cn/';
  const format = value => value ? new Date(value).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai',hour12:false}) : '尚未完成';
  function render(page, query='') {
    if(page!==currentPage || query!==currentQuery) expanded=false;
    currentPage=page; currentQuery=query;
    const section = document.querySelector('#brandstarSection');
    section.hidden = !['home','hot','case','ip'].includes(page);
    if(section.hidden) return;
    const rows = data.items.filter(x => (page !== 'case' || x.is_case) && (page !== 'ip' || x.is_ip) && (!query || JSON.stringify(x).toLowerCase().includes(query.toLowerCase())));
    const stale = !data.last_success_at || Date.now() - Date.parse(data.last_success_at) > 36*60*60*1000;
    const state = data.status === 'error' ? '本次检查失败，保留上次内容' : stale ? '采集已超过 36 小时，请留意更新状态' : data.status === 'partial' ? '部分页面暂不可用，已保留可用内容' : `本次新增 ${data.added || 0} 篇`;
    section.innerHTML = `<div class="section-title"><div><h2>品牌星球精选 <span class="subtitle">每日同步</span></h2><p>从品牌实践和联名报道中找值得继续研究的内容。</p></div><a class="text-btn" href="https://www.brandstar.com.cn/" target="_blank" rel="noopener noreferrer">浏览来源 ↗</a></div><p class="footnote">最近检查 ${escape(format(data.checked_at))} · ${escape(state)}${data.status==='error'?` · 上次成功 ${escape(format(data.last_success_at))}`:''}</p><div class="brandstar-grid">${rows.slice(0,expanded?80:4).map(x=>`<article class="panel brandstar-card"><div><span class="tag">${escape(x.kind)}</span> <small>${escape(x.date)}</small></div><h3><button class="text-btn" data-brandstar="${escape(x.id)}">${escape(x.title)}</button></h3><p>${escape(x.source_excerpt || x.selection_reason)}</p><div>${x.topics.filter(t=>t!=='IP 合作'||x.is_ip).map(t=>`<span class="tag">${escape(t)}</span>`).join('')}</div><button class="text-btn" data-brandstar="${escape(x.id)}">阅读导读与原文 ↗</button></article>`).join('') || '<div class="empty">暂未收录符合当前条件的报道。云端会继续检查新内容。</div>'}</div>${rows.length>4?`<button class="outline" data-brandstar-more="true" style="margin-top:16px">${expanded?'收起':'查看全部 '+rows.length+' 篇'}</button>`:''}`;
  }
  function open(id) {
    const item=data.items.find(x=>x.id===id); if(!item)return;
    const body=`<div class="detail-content"><span class="tag">品牌星球精选 / 来源导读</span><h1 id="detailTitle">${escape(item.title)}</h1><p class="detail-caption">原文发布 ${escape(item.date)} · 收录 ${escape(format(item.collected_at))}</p><section class="detail-section"><h2>报道简介</h2><p>${escape(item.source_excerpt || '原文未提供简介，请查看完整报道。')}</p><small>上方为来源的简短介绍。</small></section><section class="detail-section"><h2>为什么收录</h2><p>${escape(item.selection_reason)}</p></section><div class="limits">这是自动筛选的来源导读，不等同于本站已完成的深度拆解。完整执行细节、图片与采访请阅读原文；未核实的用户反应和销售效果不会自动生成。</div><div class="detail-actions"><a class="outline" href="${escape(url(item.url))}" target="_blank" rel="noopener noreferrer">阅读品牌星球完整报道 ↗</a></div></div>`;
    show(body,item,false);
  }
  return {set(value){data={...value,items:Array.isArray(value.items)?value.items:[]};},render,open,more(){expanded=!expanded;render(currentPage,currentQuery);}};
})();
