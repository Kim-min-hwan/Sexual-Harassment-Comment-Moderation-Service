// 콘텐츠 스크립트에 댓글을 추출하라는 메시지를 보내는 함수
function requestCommentsExtraction() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
            // 콘텐츠 스크립트가 로드되었는지 확인하기 위해 메시지를 보냄
            chrome.tabs.sendMessage(tabs[0].id, { type: 'extract_comments' }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error('Error sending message:', chrome.runtime.lastError);
                } else {
                    console.log('Message sent successfully:', response);
                }
            });
        }
    });
}

// 10초마다 댓글 추출을 요청하는 함수 실행 설정
setInterval(requestCommentsExtraction, 5000); // 필요에 따라 간격을 조정하세요
