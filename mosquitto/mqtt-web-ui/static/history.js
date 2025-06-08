// static/history.js

document.addEventListener('DOMContentLoaded', () => {
  const liveTab = document.getElementById('tab-live');
  const histTab = document.getElementById('tab-history');
  const livePanel = document.getElementById('live-panel');
  const histPanel = document.getElementById('history-panel');
  const tableBody = document.getElementById('history-table-body');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnDownload = document.getElementById('btn-download');

  // タブ切り替え
  function switchTab(tab) {
    if (tab === 'live') {
      livePanel.style.display = '';
      histPanel.style.display = 'none';
      liveTab.classList.add('bg-blue-600');
      liveTab.classList.remove('bg-gray-700');
      histTab.classList.add('bg-gray-700');
      histTab.classList.remove('bg-blue-600');
    } else {
      livePanel.style.display = 'none';
      histPanel.style.display = '';
      histTab.classList.add('bg-blue-600');
      histTab.classList.remove('bg-gray-700');
      liveTab.classList.add('bg-gray-700');
      liveTab.classList.remove('bg-blue-600');
      loadHistory();
    }
  }

  liveTab.addEventListener('click', () => switchTab('live'));
  histTab.addEventListener('click', () => switchTab('history'));
  btnRefresh.addEventListener('click', loadHistory);
  btnDownload.addEventListener('click', () => {
    window.location.href = '/api/logs/download';
  });

  // 履歴取得＆テーブル描画
  async function loadHistory() {
    tableBody.innerHTML = '';
    try {
      const res = await fetch(`/api/logs?limit=200`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      data.forEach(entry => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="px-2 py-1 border">${entry.timestamp}</td>
          <td class="px-2 py-1 border">${entry.topic}</td>
          <td class="px-2 py-1 border"><pre class="whitespace-pre-wrap">${entry.payload}</pre></td>
        `;
        tableBody.appendChild(tr);
      });
      if (data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">履歴がありません</td></tr>';
      }
    } catch (e) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="3" class="text-red-600 text-center">Error: ${e.message}</td>
        </tr>
      `;
    }
  }

  // 初期状態は Live を表示
  switchTab('live');
});
