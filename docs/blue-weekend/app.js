(function () {
  'use strict';
  const model = window.PilotModel;
  const $ = (selector) => document.querySelector(selector);
  const demo = $('#demo');
  let state = model.initialState();
  let presenting = false;
  let slide = 0;
  let toastTimer;
  const slides = [...document.querySelectorAll('[data-slide]')];
  const names = ['提案概览', '交互体验', '对照实验', '研究依据', '试点落地'];
  const escape = (value) => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  function bubble(text, user = false) { return `<p class="bubble${user ? ' user' : ''}">${escape(text)}</p>`; }
  function choice(action, value, label, swatch = '') {
    return `<button type="button" class="choice" data-action="${action}" data-value="${value}">${swatch ? `<span class="swatch" style="background:${swatch}" aria-hidden="true"></span>` : ''}${escape(label)}</button>`;
  }
  function landing() {
    const isB = state.creative === 'B';
    return `<div class="creative-tabs" role="group" aria-label="选择拉新素材"><button type="button" data-action="creative" data-value="A" aria-pressed="${!isB}">A · 角色介绍</button><button type="button" data-action="creative" data-value="B" aria-pressed="${isB}">B · 情境体验</button></div>
      <div class="ad-content"><p class="ad-topline"><span class="dot"></span>拉新素材样稿 / 同一示意角色</p>
      <h3 class="ad-title" id="scene-title" tabindex="-1">${isB ? '「我今天穿了蓝色。」<br>你想收到怎样的回应？' : '认识角色A。<br>从他的一个日常开始。'}</h3>
      ${isB ? '<p class="scene-note">今天有一件很小的事，想找个人说说。</p><div class="reply-preview">“蓝色。那我就在书店门口，找穿蓝色的你。”<br><span class="fine">原创示意台词 · 正式版需匹配角色设定</span></div>' : '<div class="ad-illustration"><span class="ad-envelope" aria-hidden="true">A.</span><p>现有角色占位<br><small class="fine">正式版使用审核后的官方资料</small></p></div><p class="scene-note">素材结构：角色身份 → 性格特征 → 代表性片段。人物信息与立绘待角色审核后替换。</p>'}
      <button type="button" class="button primary" data-action="start">${isB ? '从这句开始' : '进入角色体验'} <span aria-hidden="true">→</span></button><p class="fine">两版进入同一体验。此处展示创意结构，未接入投放或下载归因。</p></div>`;
  }
  function storyHeader() {
    return `<div class="chat-header"><div class="chat-person"><span class="avatar" aria-hidden="true">A</span><div><b>角色A · 示意占位</b><small>原创分支脚本 / 非AI实时生成</small></div></div><span class="chapter-label">${state.chapter + 1} / 3</span></div>
      <div class="story-mode" role="group" aria-label="选择内容组织方式"><button type="button" data-action="mode" data-value="serial" aria-pressed="${state.mode === 'serial'}">连续事件 · 实验构想</button><button type="button" data-action="mode" data-value="standalone" aria-pressed="${state.mode === 'standalone'}">独立日常 · 对照示意</button></div>
      <div class="story-progress" aria-hidden="true">${[0, 1, 2].map(i => `<span class="${i <= state.chapter ? 'current' : ''}"></span>`).join('')}</div>`;
  }
  function chapterZero() {
    const serial = state.mode === 'serial';
    let content = `<p class="story-caption">第一篇 / ${serial ? '出门之前' : '今天的颜色'}</p><h3 id="scene-title" tabindex="-1">${serial ? '把周末，留一点给见面。' : '今天，你穿了什么颜色？'}</h3><p class="scene-note">${serial ? '周末下午，你们约好在街角见面。出门前，对话框亮了起来。' : '一个独立的日常话题。后续篇章不会引用本篇的选择。'}</p>`;
    content += bubble(serial ? '快出门了？今天穿了什么颜色，我好一眼认出你。' : '今天穿了什么颜色？');
    if (!state.color) return content + '<p class="choice-label">选一个颜色，接上这句话</p><div class="choices">' + Object.entries(model.colors).map(([k, v]) => choice('color', k, v.label, v.hex)).join('') + '</div>';
    const color = model.colors[state.color].label;
    content += bubble(`今天穿了${color}。`, true);
    const replies = { blue: '蓝色。那我就在书店门口，找穿蓝色的你。', white: '白色。看见你之前，我先把位置发给你。', black: '黑色。好，我会站在门口，免得你找。' };
    content += bubble(serial ? replies[state.color] : `${color}。听起来，你已经为今天选好了一个开场。`);
    if (!state.route) {
      content += `<p class="choice-label">${serial ? '这次见面，你想怎样开始？' : '今天更想做哪件小事？'}</p><div class="choices">${choice('route', 'walk', '在街边散散步')}${choice('route', 'bookshop', '去书店坐一会儿')}</div>`;
    } else {
      content += bubble(state.route === 'walk' ? '想在街边慢慢走。' : '想去书店坐一会儿。', true);
      content += bubble(serial ? (state.route === 'walk' ? '那就不赶时间。到了给我发消息，我们从街角开始走。' : '好，靠窗那排有座位。我们先过去看看。') : '好，给自己留一点慢下来的时间。');
      content += `<button type="button" class="button primary story-next" data-action="next">查看第二篇 <span aria-hidden="true">→</span></button>`;
    }
    return content;
  }
  function chapterOne() {
    const serial = state.mode === 'serial';
    let content = `<p class="story-caption">第二篇 / ${serial ? '计划外的小雨' : '雨天小事'}</p><h3 id="scene-title" tabindex="-1">雨来得比预报早一点。</h3><p class="scene-note">${serial ? (state.route === 'bookshop' ? '往书店走的路上，雨点落在了招牌上。刚才的计划，遇到了一点变化。' : '你们刚从街角出发，小雨就落了下来。街道一下安静了。') : '今天的独立话题：如果散步时下起小雨，你会怎么办？'}</p>`;
    content += bubble(serial ? '雨不大。我们继续走，还是先到那边躲一会儿？' : '小雨天，你会继续走，还是找地方听一会儿雨？');
    if (!state.rain) return content + `<div class="choices">${choice('rain', 'continue', serial && state.route === 'bookshop' ? '继续去书店' : '继续慢慢走')}${choice('rain', 'shelter', '先去屋檐下躲雨')}</div>`;
    content += bubble(state.rain === 'shelter' ? '先躲一会儿吧。' : (serial && state.route === 'bookshop' ? '继续去书店吧。' : '想继续慢慢走。'), true);
    content += bubble(state.rain === 'shelter' ? (serial ? '这边。站里面一点，这里淋不到。等雨小一点再说。' : '屋檐下听雨，确实适合留一点空白给自己。') : (serial ? '好，跟上。前面有一小段积水，走这边。' : '那就慢一点。留意积水，也留意路边的风景。'));
    return content + '<button type="button" class="button primary story-next" data-action="next">查看第三篇 <span aria-hidden="true">→</span></button>';
  }
  function chapterTwo() {
    const serial = state.mode === 'serial';
    const recap = model.recap(state);
    let content = `<p class="story-caption">第三篇 / ${serial ? '回去以后' : '街角的光'}</p><h3 id="scene-title" tabindex="-1">${state.memory ? '这一篇，到这里刚刚好。' : '有一个瞬间，想再说一遍。'}</h3>`;
    if (!state.memory) {
      content += `<p class="scene-note">${serial ? '回到家，手机收到一条消息。那段被雨改变的下午，又被轻轻提起。' : '今天的独立话题：一场雨过后，哪个画面让你停了一下？'}</p>`;
      content += bubble(serial ? `今天你穿着${recap.color}，我们${recap.place}。现在想起来，你最想留下的是哪个瞬间？` : '雨后的街角，你更想记住声音，还是光？');
      return content + `<div class="choices">${choice('memory', 'sound', '雨落下来的声音')}${choice('memory', 'light', '雨后街角的光')}</div>`;
    }
    content += '<p class="complete-label"><span class="dot"></span>三篇示意内容已体验完</p>';
    content += `<div class="memory-card"><span class="mini-label">${serial ? '这一页，属于刚才的选择' : '三篇独立日常 / 体验结束'}</span><h4>${serial ? recap.color + '的周末' : '留一个瞬间给今天'}</h4><p>${serial ? `穿了${recap.color}。<br>原本想${state.route === 'bookshop' ? '去书店坐坐' : '在街边散步'}，后来我们${recap.place}。<br>想留下的是：${recap.detail}。` : `今天想留下的是：${recap.detail}。<br>这篇独立内容没有引用前两篇的选择。`}</p><small>由本页选择拼成的固定脚本；不代表游戏已有跨篇记忆能力。</small></div>`;
    content += bubble(serial ? '那就记在这一页。下次见面，再添一个新的瞬间。' : '把它记下来吧。今天也有一件值得留下的小事。');
    content += '<button type="button" class="button primary story-next" data-action="experiment">看怎样验证留存 <span aria-hidden="true">→</span></button><button type="button" class="quiet-button" data-action="restart" style="display:block;margin:13px auto 0">重新选择，看看故事怎样变化</button>';
    return content;
  }
  function renderDemo(focus = false) {
    demo.innerHTML = state.started ? storyHeader() + '<div class="story-body">' + [chapterZero, chapterOne, chapterTwo][state.chapter]() + '</div>' : landing();
    const journey = state.started ? Math.min(2, state.chapter) : 0;
    document.querySelectorAll('[data-journey]').forEach(el => el.classList.toggle('active', Number(el.dataset.journey) === journey));
    const insights = [
      '观察用户能否从素材承诺接上第一次互动。正式版必须使用人设一致、产品能够承接的台词。',
      '给用户一个可以表达偏好的情境，让角色在事件中表现性格。这里的分支仅在本页运行。',
      '共同经历被具体回顾，可能形成继续了解角色的理由。还需要真实跨日互动与D7数据来验证。'
    ];
    $('#operator-insight').textContent = !state.started ? '比较同一角色的两种开场，观察哪一种能让用户真正开始互动。' : state.mode === 'standalone' ? '对照示意：同样有三个话题，但彼此独立。正式实验仍需统一篇幅、质量、入口与提醒频次。' : insights[state.chapter];
    if (focus) $('#scene-title')?.focus({ preventScroll: true });
  }
  demo.addEventListener('click', event => {
    const target = event.target.closest('button[data-action]');
    if (!target) return;
    const { action, value } = target.dataset;
    if (action === 'creative' && ['A', 'B'].includes(value)) state.creative = value;
    else if (action === 'start') state.started = true;
    else if (action === 'mode' && ['serial', 'standalone'].includes(value)) state = { ...model.initialState(), started: true, mode: value, creative: state.creative };
    else if (action === 'color' && model.colors[value]) state.color = value;
    else if (action === 'route' && ['walk', 'bookshop'].includes(value)) state.route = value;
    else if (action === 'rain' && ['continue', 'shelter'].includes(value)) state.rain = value;
    else if (action === 'memory' && ['sound', 'light'].includes(value)) state.memory = value;
    else if (action === 'next' && ((state.chapter === 0 && state.color && state.route) || (state.chapter === 1 && state.rain))) state.chapter += 1;
    else if (action === 'restart') state = { ...model.initialState(), started: true, mode: state.mode, creative: state.creative };
    else if (action === 'experiment') { navigate('experiment'); return; }
    renderDemo(true);
  });
  $('#reset-demo').addEventListener('click', () => { state = model.initialState(); renderDemo(true); });
  const pct = value => (value * 100).toFixed(1) + '%';
  const pp = value => (value > 0 ? '+' : '') + (value * 100).toFixed(1);
  function updateMetrics() {
    const values = ['#n-a', '#r-a', '#n-b', '#r-b'].map(selector => $(selector).value.trim() === '' ? NaN : Number($(selector).value));
    const result = model.rateDifference(...values);
    if (result.error) { $('#metric-output').innerHTML = `<p class="error">${result.error}</p>`; return; }
    $('#metric-output').innerHTML = `<div class="rates"><span>A组 <b>${pct(result.a)}</b></span><span>B组 <b>${pct(result.b)}</b></span><span>差值 <b>${pp(result.delta)}</b> 个百分点</span></div><p>差值的近似95%区间：${pp(result.low)} 至 ${pp(result.high)} 个百分点。</p><p>${result.containsZero ? '区间包含0，当前演算不足以说明哪组更好。' : '区间未包含0，也须核对分组、样本计划和业务价值，不能据此直接扩量。'}${result.sparse ? ' 部分计数很小，区间仅供参考。' : ''}</p><p class="fine">独立二项样本的Wilson / Newcombe近似。仅用于理解不确定性。</p>`;
  }
  $('#metric-form').addEventListener('input', updateMetrics);
  $('#metric-form').addEventListener('submit', event => event.preventDefault());
  function showSlide(index) {
    slide = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((section, i) => section.classList.toggle('current-slide', i === slide));
    $('#slide-status').textContent = String(slide + 1).padStart(2, '0') + ' / 05';
    $('#slide-name').textContent = names[slide];
    $('#prev-slide').disabled = slide === 0;
    $('#next-slide').disabled = slide === slides.length - 1;
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
  function setPresent(value) {
    presenting = value;
    document.body.classList.toggle('presenting', value);
    $('#present-bar').hidden = !value;
    $('#present-toggle').textContent = value ? '退出演示 ×' : '开始演示 ↗';
    $('#present-toggle').setAttribute('aria-pressed', String(value));
    if (value) showSlide(slide);
    else slides[slide].scrollIntoView({ behavior: 'instant', block: 'start' });
  }
  function navigate(id) {
    const section = document.getElementById(id);
    if (!section) return;
    if (presenting) showSlide(Number(section.dataset.slide));
    else section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  $('#present-toggle').addEventListener('click', () => setPresent(!presenting));
  $('#exit-present').addEventListener('click', () => setPresent(false));
  $('#prev-slide').addEventListener('click', () => showSlide(slide - 1));
  $('#next-slide').addEventListener('click', () => showSlide(slide + 1));
  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', event => {
    if (presenting && document.getElementById(link.hash.slice(1))?.hasAttribute('data-slide')) { event.preventDefault(); navigate(link.hash.slice(1)); }
  }));
  const dialog = $('#notes-dialog');
  const openNotes = () => { if (!dialog.open) dialog.showModal(); };
  $('#show-notes').addEventListener('click', openNotes);
  $('#present-notes').addEventListener('click', openNotes);
  $('#close-notes').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const box = dialog.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close(); } });
  document.addEventListener('keydown', event => {
    if (!presenting || dialog.open || event.target.matches('input,textarea,select,[contenteditable="true"]')) return;
    if (event.key === 'ArrowRight') { event.preventDefault(); showSlide(slide + 1); }
    if (event.key === 'ArrowLeft') { event.preventDefault(); showSlide(slide - 1); }
    if (event.key === 'Escape') setPresent(false);
  });
  function notify(message) { const el = $('#toast'); el.textContent = message; el.hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => { el.hidden = true; }, 2800); }
  $('#download-notes').addEventListener('click', () => {
    const text = '蓝色的周末｜Yuanyuan 内容运营面试讲稿\n概念提案，未开展真实业务实验。\n\n' + [...document.querySelectorAll('#notes-content article')].map(el => el.innerText).join('\n\n');
    const url = URL.createObjectURL(new Blob(['\uFEFF', text], { type: 'text/plain;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = '蓝色的周末-3分钟面试讲稿.txt'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000); notify('讲稿已准备下载');
  });
  $('#print-page').addEventListener('click', () => window.print());
  renderDemo();
  updateMetrics();
})();
