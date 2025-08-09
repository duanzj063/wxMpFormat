// 微信文章格式化与海报生成系统 - 前端交互逻辑

// 全局变量
let currentPosterHtml = '';
let systemStatus = {
    api_configured: false,
    ai_service: 'unknown',
    last_check: null
};

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 应用初始化
function initializeApp() {
    // 绑定事件监听器
    bindEventListeners();
    
    // 检查系统状态
    checkSystemStatus();
    
    // 初始化字符计数
    updateCharCount();
    
    // 显示欢迎消息
    showToast('系统已就绪', '欢迎使用微信文章格式化与海报生成系统！', 'success');
}

// 绑定事件监听器
function bindEventListeners() {
    // 文章输入区域字符计数
    const articleInput = document.getElementById('articleContent');
    if (articleInput) {
        articleInput.addEventListener('input', updateCharCount);
        articleInput.addEventListener('paste', function() {
            setTimeout(updateCharCount, 100);
        });
    }
    
    // 格式化按钮
    const formatBtn = document.getElementById('formatBtn');
    if (formatBtn) {
        formatBtn.addEventListener('click', formatArticle);
    }
    
    // 生成海报按钮
    const generatePosterBtn = document.getElementById('generatePosterBtn');
    if (generatePosterBtn) {
        generatePosterBtn.addEventListener('click', generatePoster);
    }
    
    // 下载海报按钮
    const downloadPosterBtn = document.getElementById('downloadPosterBtn');
    if (downloadPosterBtn) {
        downloadPosterBtn.addEventListener('click', downloadPoster);
    }
    
    // 清空按钮
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearAll);
    }
    
    // 复制按钮
    const copyBtn = document.getElementById('copyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyFormattedText);
    }
    
    // 系统状态刷新按钮
    const refreshStatusBtn = document.getElementById('refreshStatusBtn');
    if (refreshStatusBtn) {
        refreshStatusBtn.addEventListener('click', checkSystemStatus);
    }
    
    // 配置页面相关事件
    bindConfigEvents();
}

// 绑定配置页面事件
function bindConfigEvents() {
    // 保存配置按钮
    const saveConfigBtn = document.getElementById('saveConfigBtn');
    if (saveConfigBtn) {
        saveConfigBtn.addEventListener('click', saveConfig);
    }
    
    // 测试连接按钮
    const testConnectionBtn = document.getElementById('testConnectionBtn');
    if (testConnectionBtn) {
        testConnectionBtn.addEventListener('click', testConnection);
    }
    
    // 重置配置按钮
    const resetConfigBtn = document.getElementById('resetConfigBtn');
    if (resetConfigBtn) {
        resetConfigBtn.addEventListener('click', resetConfig);
    }
    
    // API密钥显示切换
    const toggleApiKeyBtn = document.getElementById('toggleApiKeyBtn');
    if (toggleApiKeyBtn) {
        toggleApiKeyBtn.addEventListener('click', toggleApiKeyVisibility);
    }
}

// 更新字符计数
function updateCharCount() {
    const articleInput = document.getElementById('articleContent');
    const charCount = document.getElementById('charCount');
    
    if (articleInput && charCount) {
        const count = articleInput.value.length;
        charCount.textContent = `${count} 字符`;
        
        // 根据字符数量改变颜色
        if (count > 10000) {
            charCount.style.color = '#dc3545';
        } else if (count > 5000) {
            charCount.style.color = '#fd7e14';
        } else {
            charCount.style.color = '#6c757d';
        }
    }
}

// 格式化文章
async function formatArticle() {
    const articleInput = document.getElementById('articleContent');
    const formatBtn = document.getElementById('formatBtn');
    const loading = formatBtn.querySelector('.loading');
    const preview = document.getElementById('formattedPreview');
    const useAiFormat = document.getElementById('useAiFormat');
    
    if (!articleInput || !articleInput.value.trim()) {
        showToast('输入错误', '请输入要格式化的文章内容', 'warning');
        return;
    }
    
    // 显示加载状态
    setLoadingState(formatBtn, loading, true);
    
    try {
        const response = await fetch('/api/format-article', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: articleInput.value,
                use_ai: useAiFormat ? useAiFormat.checked : false
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (preview) {
                preview.textContent = data.formatted_content;
                preview.classList.add('fade-in');
            }
            const method = data.method || '规则排版';
            showToast('格式化成功', `文章已成功使用${method}格式化为Markdown`, 'success');
        } else {
            throw new Error(data.error || '格式化失败');
        }
    } catch (error) {
        console.error('格式化错误:', error);
        showToast('格式化失败', error.message || '请检查网络连接或稍后重试', 'error');
    } finally {
        setLoadingState(formatBtn, loading, false);
    }
}

// 生成海报
async function generatePoster() {
    const articleInput = document.getElementById('articleContent');
    const posterType = document.getElementById('posterType');
    const generateBtn = document.getElementById('generatePosterBtn');
    const loading = document.getElementById('posterLoading');
    const preview = document.getElementById('posterPreview');
    const downloadBtn = document.getElementById('downloadPosterBtn');
    
    if (!articleInput || !articleInput.value.trim()) {
        showToast('输入错误', '请输入文章内容以生成海报', 'warning');
        return;
    }
    
    // 显示加载状态
    setLoadingState(generateBtn, loading, true);
    
    try {
        const response = await fetch('/api/generate_poster', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: articleInput.value,
                poster_type: posterType ? posterType.value : 'xiaohongshu'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPosterHtml = data.html_content;
            
            if (preview) {
                // 创建iframe来预览海报
                const iframe = document.createElement('iframe');
                iframe.style.width = '100%';
                iframe.style.height = '400px';
                iframe.style.border = 'none';
                iframe.style.borderRadius = '5px';
                
                preview.innerHTML = '';
                preview.appendChild(iframe);
                
                // 写入HTML内容
                iframe.contentDocument.open();
                iframe.contentDocument.write(currentPosterHtml);
                iframe.contentDocument.close();
                
                preview.classList.add('fade-in');
            }
            
            // 启用下载按钮
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.classList.remove('btn-secondary');
                downloadBtn.classList.add('btn-success');
            }
            
            showToast('生成成功', '海报已成功生成，可以预览和下载', 'success');
        } else {
            throw new Error(data.error || '生成失败');
        }
    } catch (error) {
        console.error('海报生成错误:', error);
        showToast('生成失败', error.message || '请检查AI配置或稍后重试', 'error');
    } finally {
        setLoadingState(generateBtn, loading, false);
    }
}

// 下载海报
function downloadPoster() {
    if (!currentPosterHtml) {
        showToast('下载错误', '请先生成海报', 'warning');
        return;
    }
    
    try {
        // 创建下载链接
        const blob = new Blob([currentPosterHtml], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = `poster_${new Date().getTime()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('下载成功', '海报HTML文件已保存到本地', 'success');
    } catch (error) {
        console.error('下载错误:', error);
        showToast('下载失败', '文件下载失败，请重试', 'error');
    }
}

// 清空所有内容
function clearAll() {
    if (confirm('确定要清空所有内容吗？此操作不可撤销。')) {
        // 清空输入
        const articleInput = document.getElementById('articleContent');
        if (articleInput) {
            articleInput.value = '';
        }
        
        // 重置AI排版选项
        const useAiFormat = document.getElementById('useAiFormat');
        if (useAiFormat) {
            useAiFormat.checked = false;
        }
        
        // 清空预览
        const formattedPreview = document.getElementById('formattedPreview');
        if (formattedPreview) {
            formattedPreview.textContent = '格式化后的内容将在这里显示...';
        }
        
        const posterPreview = document.getElementById('posterPreview');
        if (posterPreview) {
            posterPreview.innerHTML = '<div class="text-muted"><i class="fas fa-image fa-3x mb-3"></i><br>海报预览将在这里显示</div>';
        }
        
        // 重置下载按钮
        const downloadBtn = document.getElementById('downloadPosterBtn');
        if (downloadBtn) {
            downloadBtn.disabled = true;
            downloadBtn.classList.remove('btn-success');
            downloadBtn.classList.add('btn-secondary');
        }
        
        // 清空当前海报HTML
        currentPosterHtml = '';
        
        // 更新字符计数
        updateCharCount();
        
        showToast('清空成功', '所有内容已清空', 'info');
    }
}

// 复制格式化文本
function copyFormattedText() {
    const preview = document.getElementById('formattedPreview');
    
    if (!preview || !preview.textContent.trim() || preview.textContent.includes('格式化后的内容将在这里显示')) {
        showToast('复制错误', '没有可复制的格式化内容', 'warning');
        return;
    }
    
    try {
        navigator.clipboard.writeText(preview.textContent).then(() => {
            showToast('复制成功', '格式化内容已复制到剪贴板', 'success');
        }).catch(() => {
            // 降级方案
            const textArea = document.createElement('textarea');
            textArea.value = preview.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('复制成功', '格式化内容已复制到剪贴板', 'success');
        });
    } catch (error) {
        console.error('复制错误:', error);
        showToast('复制失败', '复制到剪贴板失败', 'error');
    }
}

// 检查系统状态
async function checkSystemStatus() {
    const refreshBtn = document.getElementById('refreshStatusBtn');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const lastCheck = document.getElementById('lastCheck');
    
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        systemStatus = data;
        
        // 更新状态显示
        if (statusIndicator && statusText) {
            if (data.api_configured) {
                statusIndicator.className = 'status-indicator status-success';
                statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i> 已配置';
                statusText.textContent = `AI服务: ${data.ai_service || '未知'}`;
            } else {
                statusIndicator.className = 'status-indicator status-warning';
                statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i> 未配置';
                statusText.textContent = '请前往配置页面设置AI服务';
            }
        }
        
        // 更新检查时间
        if (lastCheck) {
            lastCheck.textContent = new Date().toLocaleString();
        }
        
    } catch (error) {
        console.error('状态检查错误:', error);
        
        if (statusIndicator && statusText) {
            statusIndicator.className = 'status-indicator status-error';
            statusIndicator.innerHTML = '<i class="fas fa-times-circle"></i> 错误';
            statusText.textContent = '无法连接到服务器';
        }
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
        }
    }
}

// 设置加载状态
function setLoadingState(button, loading, isLoading) {
    if (button) {
        button.disabled = isLoading;
    }
    
    if (loading) {
        if (isLoading) {
            loading.classList.add('show');
        } else {
            loading.classList.remove('show');
        }
    }
}

// 显示Toast通知
function showToast(title, message, type = 'info') {
    // 创建toast容器（如果不存在）
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // 创建toast元素
    const toastId = 'toast_' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas ${getToastIcon(type)} me-2 text-${getToastColor(type)}"></i>
                <strong class="me-auto">${title}</strong>
                <small class="text-muted">刚刚</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // 显示toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: type === 'error' ? 8000 : 5000
    });
    
    toast.show();
    
    // 自动清理
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// 获取Toast图标
function getToastIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// 获取Toast颜色
function getToastColor(type) {
    const colors = {
        success: 'success',
        error: 'danger',
        warning: 'warning',
        info: 'info'
    };
    return colors[type] || colors.info;
}

// 配置页面相关函数

// 保存配置
async function saveConfig() {
    const form = document.getElementById('configForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const config = {
        api_url: formData.get('api_url'),
        api_key: formData.get('api_key'),
        ai_model: formData.get('ai_model')
    };
    
    const saveBtn = document.getElementById('saveConfigBtn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
    }
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('保存成功', '配置已保存，系统将使用新的设置', 'success');
        } else {
            throw new Error(data.error || '保存失败');
        }
    } catch (error) {
        console.error('配置保存错误:', error);
        showToast('保存失败', error.message || '请检查输入并重试', 'error');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save"></i> 保存配置';
        }
    }
}

// 测试连接
async function testConnection() {
    const testBtn = document.getElementById('testConnectionBtn');
    if (testBtn) {
        testBtn.disabled = true;
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 测试中...';
    }
    
    try {
        const response = await fetch('/api/test_connection', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('连接成功', 'AI服务连接正常，可以正常使用', 'success');
        } else {
            throw new Error(data.error || '连接失败');
        }
    } catch (error) {
        console.error('连接测试错误:', error);
        showToast('连接失败', error.message || '请检查配置或网络连接', 'error');
    } finally {
        if (testBtn) {
            testBtn.disabled = false;
            testBtn.innerHTML = '<i class="fas fa-plug"></i> 测试连接';
        }
    }
}

// 重置配置
function resetConfig() {
    if (confirm('确定要重置所有配置吗？此操作将清空所有设置。')) {
        const form = document.getElementById('configForm');
        if (form) {
            form.reset();
            showToast('重置成功', '配置已重置，请重新设置', 'info');
        }
    }
}

// 切换API密钥显示
function toggleApiKeyVisibility() {
    const apiKeyInput = document.getElementById('api_key');
    const toggleBtn = document.getElementById('toggleApiKeyBtn');
    
    if (apiKeyInput && toggleBtn) {
        if (apiKeyInput.type === 'password') {
            apiKeyInput.type = 'text';
            toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
        } else {
            apiKeyInput.type = 'password';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        }
    }
}

// 工具函数

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化时间
function formatTime(date) {
    return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }).format(date);
}

// 验证URL格式
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// 验证API密钥格式（简单验证）
function isValidApiKey(key) {
    return key && key.length >= 10 && /^[a-zA-Z0-9\-_]+$/.test(key);
}

// 导出函数（如果需要在其他脚本中使用）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatArticle,
        generatePoster,
        downloadPoster,
        showToast,
        checkSystemStatus
    };
}