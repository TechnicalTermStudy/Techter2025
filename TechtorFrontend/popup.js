document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('toggleButton');
    const statusContainer = document.getElementById('statusContainer');
    const statusText = statusContainer.querySelector('.status-text');

    // 读取存储的状态
    chrome.storage.local.get('isEnabled', function(data) {
        const isEnabled = data.isEnabled !== false;  // 默认为启用
        updateUI(isEnabled);
    });

    button.addEventListener('click', function() {
        chrome.storage.local.get('isEnabled', function(data) {
            const isEnabled = !data.isEnabled;
            chrome.storage.local.set({ isEnabled: isEnabled }, function() {
                updateUI(isEnabled);
                // 通知 content script 更新状态
                chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                    chrome.tabs.sendMessage(tabs[0].id, { isEnabled: isEnabled });
                });
            });
        });
    });

    function updateUI(isEnabled) {
        // 更新按钮
        button.textContent = isEnabled ? 'Disable Extension' : 'Enable Extension';
        button.className = isEnabled ? 'disable' : 'enable';
        
        // 更新状态指示器
        statusContainer.className = 'status ' + (isEnabled ? 'active' : 'inactive');
        statusText.textContent = isEnabled ? 'Extension is enabled' : 'Extension is disabled';
    }
});
