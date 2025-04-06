// content.js 에 댓글 추출 요청
function requestCommentsExtraction() {
    chrome.tabs.query({ activate: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            // content.js가 로드되었는지 확인
            chrome.tabs.sendMessage(tabs[0].id, { type: 'extract_comments' }, (response) => {
                if (response) {
                    console.log('Message sent successfully:', response);
                } else {
                    console.error('Error sending message:', chrome.runtime.lastError);
                }
            });
        }
    });
}

// N(ms)마다 댓글 추출 요청
setInterval(requestCommentsExtraction, 5000);