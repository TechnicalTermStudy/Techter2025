chrome.runtime.onInstalled.addListener(function() {
    console.log("Extension installed");
});

chrome.runtime.onSuspend.addListener(function() {
    console.log("Extension unloaded");
});
