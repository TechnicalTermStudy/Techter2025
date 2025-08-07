let currentTooltip = null;
let isEnabled = false;

const privacyLink = document.querySelector('a[data-cy="privacy-policy-link-detail-0"]');
if (privacyLink) {
    const descriptionDiv = document.querySelector('div[data-cy="skill-product-description-see-more"]');
    const descriptionText = descriptionDiv.innerText;
    const titleDiv = document.querySelector('div[data-cy="skill-title"]');
    const titleText = titleDiv.innerText;
    // const categoryDivs = document.querySelectorAll('div.sc-iMfspA.bdNMQs');
    // const categoryText = categoryDivs[categoryDivs.length - 1].textContent.trim();
    // console.log("Category content:", categoryText);
    console.log("Title content:", titleText);
    console.log("Description content:", descriptionText);
    chrome.storage.local.set({ description: descriptionText }, function() {
        console.log('Description saved in Chrome Storage:', descriptionText);
    });
    chrome.storage.local.set({ skillName: titleText }, function() {
        console.log('Title saved in Chrome Storage:', titleText);
    });
    // chrome.storage.local.set({ category: categoryText }, function() {
    //     console.log('Category saved in Chrome Storage:', categoryText);
    // });
/*     privacyLink.addEventListener('click', function(event) {
        // Log the click action
        console.log("Developer Privacy Policy link clicked!");


        // Optionally, prevent the default behavior if needed
        // event.preventDefault();
    }); */
} else {
    console.log("Link not found.");
}

function makeDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    element.onmousedown = function(event) {
        event.preventDefault();
        pos3 = event.clientX;
        pos4 = event.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    };

    function elementDrag(event) {
        event.preventDefault();
        pos1 = pos3 - event.clientX;
        pos2 = pos4 - event.clientY;
        pos3 = event.clientX;
        pos4 = event.clientY;
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

function createTooltip(term, explanation, posX, posY) {
    removeTooltip(); 

    var tooltip = document.createElement('div');
    tooltip.style.position = 'absolute';
    tooltip.style.left = `${posX}px`;
    tooltip.style.top = `${posY + 20}px`;
    tooltip.style.padding = '16px';
    tooltip.style.background = '#f8f9fa';
    tooltip.style.border = '2px solid #4a90e2';
    tooltip.style.borderRadius = '8px';
    tooltip.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    tooltip.style.zIndex = '10000';
    tooltip.style.cursor = 'move';
    tooltip.style.width = '320px';
    tooltip.style.maxWidth = '400px';
    tooltip.style.wordWrap = 'break-word';
    tooltip.style.fontSize = '14px';
    tooltip.style.lineHeight = '1.6';
    tooltip.style.color = '#2c3e50';
    tooltip.style.fontFamily = 'Arial, sans-serif';
    
    // 
    var header = document.createElement('div');
    header.style.borderBottom = '1px solid #e0e0e0';
    header.style.marginBottom = '12px';
    header.style.paddingBottom = '8px';
    header.style.fontWeight = 'bold';
    header.style.color = '#4a90e2';
    header.style.fontSize = '16px';
    header.textContent = term;  // 
    tooltip.appendChild(header);
    
    // 
    var textContainer = document.createElement('div');
    textContainer.style.marginBottom = '12px';
    textContainer.style.minHeight = '100px';  // 
    
    // 
    var loadingSpan = document.createElement('span');
    loadingSpan.style.display = 'inline-block';
    loadingSpan.style.width = '2px';
    loadingSpan.style.height = '16px';
    loadingSpan.style.background = '#4a90e2';
    loadingSpan.style.animation = 'blink 1s infinite';
    loadingSpan.style.verticalAlign = 'middle';
    loadingSpan.style.marginLeft = '4px';
    
    // 
    var style = document.createElement('style');
    style.textContent = `
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    textContainer.appendChild(loadingSpan);
    tooltip.appendChild(textContainer);

    // 
    var buttonContainer = document.createElement('div');
    buttonContainer.style.borderTop = '1px solid #e0e0e0';
    buttonContainer.style.marginTop = '12px';
    buttonContainer.style.paddingTop = '8px';
    buttonContainer.style.textAlign = 'right';

    var closeButton = document.createElement('button');
    closeButton.textContent = 'Close';
    closeButton.style.padding = '6px 12px';
    closeButton.style.border = '1px solid #4a90e2';
    closeButton.style.borderRadius = '4px';
    closeButton.style.background = '#4a90e2';
    closeButton.style.color = 'white';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontSize = '13px';
    closeButton.style.transition = 'background-color 0.2s';
    
    // 
    closeButton.onmouseover = function() {
        this.style.background = '#357abd';
    };
    closeButton.onmouseout = function() {
        this.style.background = '#4a90e2';
    };
    
    closeButton.onclick = function(event) {
        event.stopPropagation();
        tooltip.remove();
        currentTooltip = null;
    };
    
    buttonContainer.appendChild(closeButton);
    tooltip.appendChild(buttonContainer);

    document.body.appendChild(tooltip);
    currentTooltip = tooltip;

    makeDraggable(tooltip);
}

function removeTooltip() {
    if (currentTooltip) {
        document.body.removeChild(currentTooltip);
        currentTooltip = null;
    }
}
function getTerm(event) {
    if (currentTooltip && currentTooltip.contains(event.target) && event.target.tagName === 'BUTTON') {
        return; // Do not create a new tooltip if clicking on any button within the current tooltip
    }

    if (event.button === 0) {
        var selection = window.getSelection();
        var selectedText = selection.toString().trim();
        var container;
        if (selectedText.length > 0) {
            if (selection.rangeCount > 0) {
                var range = selection.getRangeAt(0);
        
                if (selectedText !== '') {
                    container = range.commonAncestorContainer;
        
                    // 
                    if (container.nodeType !== 1) {
                        container = container.parentNode;
                    }
        
                    // 
                    while (container != null && container.nodeName !== 'P') {
                        container = container.parentNode;
                    }
                }
            }
            
            // 
            createTooltip(selectedText, "", event.pageX, event.pageY);
            
            // 
            chrome.storage.local.get(['skillName', 'description'], function(data) {
                // 从服务器获取数据
                fetch('http://127.0.0.1:5000/data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        term: selectedText,
                        context: container ? container.textContent : '',
                        skillTitle: data.skillName || '',
                        description: data.description || ''
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Server response:', data); // 
                    
                    //
                    if (currentTooltip) {
                        const textContainer = currentTooltip.querySelector('div:nth-child(2)'); // 
                        if (textContainer) {
                            // 
                            textContainer.innerHTML = '';
                            
                            // 
                            const textSpan = document.createElement('span');
                            textSpan.style.display = 'block';
                            textContainer.appendChild(textSpan);
                            
                            // 使用 received 字段作为解释内容
                            const explanation = data.received || '无法获取解释';
                            
                            // 实现打字机效果
                            let index = 0;
                            const typeWriter = () => {
                                if (index < explanation.length) {
                                    textSpan.textContent += explanation.charAt(index);
                                    index++;
                                    setTimeout(typeWriter, 30);
                                }
                            };
                            typeWriter();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (currentTooltip) {
                        const textContainer = currentTooltip.querySelector('div:nth-child(2)'); // 获取第二个 div（内容容器）
                        if (textContainer) {
                            textContainer.innerHTML = '抱歉，获取解释时出现错误，请稍后重试。';
                        }
                    }
                });
            });
            
            // 记录选择的信息（用于调试）
            console.log("Selected text:", selectedText);
            console.log("Context:", container ? container.textContent : '');
        }
    }
}
chrome.storage.local.get('isEnabled', function(data) {
    isEnabled = data.isEnabled !== false;  // 默认为启用
    if (isEnabled) {
        document.addEventListener('mouseup', getTerm);
    }
});

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (sender.tab) {
        // 消息来自 content script 或 background
        console.log("Message from content script or background");
    } else {
        // 消息来自 popup
        if (message.isEnabled !== undefined) {
            if (message.isEnabled) {
                // 启用功能
                enableFunctionality();
            } else {
                // 禁用功能
                disableFunctionality();
            }
        }
        console.log("Message from popup");
    }
});

function enableFunctionality() {
    console.log("open");
    document.addEventListener('mouseup', getTerm);
}

function disableFunctionality() {
    console.log("close");
    document.removeEventListener('mouseup', getTerm);
}
