// 校园跑步数据生成器 - Web前端

let currentJobId = null;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', async () => {
    initDates();
    initTabs();
    await loadTracks();
    await loadTemplates();
    initForms();
});

// 初始化日期默认值
function initDates() {
    const today = new Date();
    const weekLater = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    const dateFormat = (d) => d.toISOString().split('T')[0];

    document.getElementById('daily-start-date').value = dateFormat(today);
    document.getElementById('daily-end-date').value = dateFormat(weekLater);
    document.getElementById('total-start-date').value = dateFormat(today);
    document.getElementById('total-end-date').value = dateFormat(weekLater);
    document.getElementById('single-date').value = dateFormat(today);
}

// 初始化Tab切换
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const modeContents = document.querySelectorAll('.mode-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const mode = button.dataset.mode;

            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            modeContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${mode}-mode`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// 加载轨迹列表
async function loadTracks() {
    try {
        const response = await fetch('/api/tracks');
        if (!response.ok) throw new Error('加载轨迹失败');

        const tracks = await response.json();
        const select = document.getElementById('track-select');
        select.innerHTML = tracks.map(t =>
            `<option value="${t.id}">${t.name} (${t.lap_distance_km}km/圈)</option>`
        ).join('');
    } catch (error) {
        showMessage('加载轨迹列表失败: ' + error.message, 'error');
    }
}

// 加载模板列表
async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        if (!response.ok) throw new Error('加载模板失败');

        const templates = await response.json();
        const select = document.getElementById('template-select');
        select.innerHTML = '<option value="">不使用模板</option>' +
            templates.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
    } catch (error) {
        showMessage('加载模板列表失败: ' + error.message, 'error');
    }
}

// 初始化表单提交
function initForms() {
    document.getElementById('daily-form').addEventListener('submit', handleDailySubmit);
    document.getElementById('total-form').addEventListener('submit', handleTotalSubmit);
    document.getElementById('single-form').addEventListener('submit', handleSingleSubmit);
    document.getElementById('download-btn').addEventListener('click', downloadFiles);
}

// 处理每日模式提交
async function handleDailySubmit(e) {
    e.preventDefault();
    const data = collectDailyFormData();
    await generate('daily', data);
}

// 处理总公里数模式提交
async function handleTotalSubmit(e) {
    e.preventDefault();
    const data = collectTotalFormData();
    await generate('total', data);
}

// 处理单文件模式提交
async function handleSingleSubmit(e) {
    e.preventDefault();
    const data = collectSingleFormData();
    await generate('single', data);
}

// 收集每日表单数据
function collectDailyFormData() {
    const trackId = document.getElementById('track-select').value;
    const templateId = document.getElementById('template-select').value;

    return {
        track_id: trackId,
        template_id: templateId || undefined,
        start_date: document.getElementById('daily-start-date').value,
        end_date: document.getElementById('daily-end-date').value,
        min_km: parseFloat(document.getElementById('daily-min-km').value),
        max_km: parseFloat(document.getElementById('daily-max-km').value),
        min_pace: parseFloat(document.getElementById('daily-min-pace').value),
        max_pace: parseFloat(document.getElementById('daily-max-pace').value),
        start_hour_min: parseInt(document.getElementById('daily-start-hour-min').value),
        start_hour_max: parseInt(document.getElementById('daily-start-hour-max').value),
        output_dir: document.getElementById('daily-output-dir').value,
        include_track: !document.getElementById('daily-no-track').checked,
        apply_correction: !document.getElementById('daily-no-correction').checked,
        enable_pace_fluctuation: !document.getElementById('daily-no-fluctuation').checked,
    };
}

// 收集总公里数表单数据
function collectTotalFormData() {
    const trackId = document.getElementById('track-select').value;
    const templateId = document.getElementById('template-select').value;

    return {
        track_id: trackId,
        template_id: templateId || undefined,
        start_date: document.getElementById('total-start-date').value,
        end_date: document.getElementById('total-end-date').value,
        total_km: parseFloat(document.getElementById('total-km').value),
        weekend_factor: parseFloat(document.getElementById('total-weekend-factor').value),
        min_daily_km: parseFloat(document.getElementById('total-min-daily').value),
        max_daily_km: parseFloat(document.getElementById('total-max-daily').value),
        rest_days_per_week: parseInt(document.getElementById('total-rest-days').value),
        min_pace: parseFloat(document.getElementById('total-min-pace').value),
        max_pace: parseFloat(document.getElementById('total-max-pace').value),
        output_dir: document.getElementById('total-output-dir').value,
        include_track: !document.getElementById('total-no-track').checked,
        apply_correction: !document.getElementById('total-no-correction').checked,
        enable_pace_fluctuation: !document.getElementById('total-no-fluctuation').checked,
    };
}

// 收集单文件表单数据
function collectSingleFormData() {
    const trackId = document.getElementById('track-select').value;
    const templateId = document.getElementById('template-select').value;
    const pace = document.getElementById('single-pace').value;

    return {
        track_id: trackId,
        template_id: templateId || undefined,
        date: document.getElementById('single-date').value,
        distance: parseFloat(document.getElementById('single-distance').value),
        pace: pace ? parseFloat(pace) : undefined,
        output_dir: document.getElementById('single-output-dir').value,
        include_track: !document.getElementById('single-no-track').checked,
        apply_correction: !document.getElementById('single-no-correction').checked,
        enable_pace_fluctuation: !document.getElementById('single-no-fluctuation').checked,
    };
}

// 调用API生成
async function generate(mode, data) {
    showMessage('正在生成...', 'loading');
    disableButtons(true);

    try {
        const response = await fetch(`/api/generate/${mode}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || '生成失败');
        }

        currentJobId = result.job_id;
        showResults(result);
        showMessage(`生成完成！共 ${result.total_files} 个文件`, 'success');

    } catch (error) {
        showMessage('生成失败: ' + error.message, 'error');
        currentJobId = null;
    } finally {
        disableButtons(false);
    }
}

// 显示结果
function showResults(result) {
    const section = document.getElementById('results-section');
    const tbody = document.getElementById('results-body');
    const downloadBtn = document.getElementById('download-btn');

    tbody.innerHTML = result.files.map(f => `
        <tr>
            <td>${f.date}</td>
            <td>${f.distance_km.toFixed(2)} km</td>
            <td>${f.pace_min_per_km.toFixed(2)} min/km</td>
            <td>${formatDuration(f.duration_seconds)}</td>
            <td>${f.calories}</td>
        </tr>
    `).join('');

    section.classList.add('show');
    downloadBtn.disabled = false;
}

// 格式化时长
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// 下载文件
function downloadFiles() {
    if (!currentJobId) return;
    window.location.href = `/api/download/${currentJobId}`;
}

// 显示消息
function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message ${type} show`;

    if (type !== 'loading') {
        setTimeout(() => {
            msg.classList.remove('show');
        }, 5000);
    }
}

// 禁用/启用按钮
function disableButtons(disabled) {
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        btn.disabled = disabled;
    });
    document.getElementById('download-btn').disabled = disabled;
}
