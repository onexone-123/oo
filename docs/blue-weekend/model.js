(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PilotModel = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const colors = { blue: { label: '蓝色', hex: '#7095b6' }, white: { label: '白色', hex: '#fffdf4' }, black: { label: '黑色', hex: '#354252' } };
  function initialState() {
    return { creative: 'B', mode: 'serial', started: false, chapter: 0, color: null, route: null, rain: null, memory: null };
  }
  function endingLocation(state) {
    if (state.rain === 'shelter') return '屋檐下看雨';
    return state.route === 'bookshop' ? '去了街角书店' : '沿着街道慢慢走';
  }
  function recap(state) {
    if (!colors[state.color] || !['walk', 'bookshop'].includes(state.route) || !['continue', 'shelter'].includes(state.rain)) {
      throw new Error('请先完成前两篇的选择。');
    }
    const detail = state.memory === 'sound' ? '雨落下来的声音' : '雨后街角的光';
    return { color: colors[state.color].label, place: endingLocation(state), detail };
  }
  function rateDifference(na, ra, nb, rb) {
    const values = [na, ra, nb, rb];
    if (values.some(x => !Number.isSafeInteger(x)) || na < 1 || nb < 1 || ra < 0 || rb < 0 || ra > na || rb > nb || na > 1000000 || nb > 1000000) {
      return { error: '请输入整数；入组人数须为1至1,000,000，活跃人数不能超过本组入组人数。' };
    }
    const a = ra / na, b = rb / nb, z = 1.959963984540054;
    function wilson(n, r) {
      const p = r / n, d = 1 + z * z / n;
      const mid = (p + z * z / (2 * n)) / d;
      const half = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d;
      return [Math.max(0, mid - half), Math.min(1, mid + half)];
    }
    const [al, au] = wilson(na, ra), [bl, bu] = wilson(nb, rb), delta = b - a;
    const low = Math.max(-1, delta - Math.sqrt((b - bl) ** 2 + (au - a) ** 2));
    const high = Math.min(1, delta + Math.sqrt((bu - b) ** 2 + (a - al) ** 2));
    return { a, b, delta, low, high, containsZero: low <= 0 && high >= 0, sparse: Math.min(ra, na - ra, rb, nb - rb) < 5 };
  }
  return { colors, initialState, recap, endingLocation, rateDifference };
});
