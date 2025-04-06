function debounce(func, timeout = 5000) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        setTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, timeout);
    };
}

let ori_comments = [];

async function handleScrollEvent(e) {
    // scroll 시 이벤트 발생
    const new_comments = extractComments();

    if (ori_comments.length < new_comments.length) {
        // 기존 댓글과 비교하여 새로 추가된 댓글만 추출
        const comments_which_need_to_be_checked = new_comments.filter((_, index) => index > ori_comments.length - 1);
        const targetComments = await getTargetCommentsFromServer(comments_which_need_to_be_checked);
        
        updateTargetComments(targetComments);
        ori_comments = new_comments;
    }
}

window.addEventListener("scroll", debounce(handleScrollEvent, 1000));


// 유튜브 페이지로부터 영상 제목 추출
function extractTitle() {
    const titleElement = document.querySelector('meta[name="title"]').getAttribute('content');
    return titleElement;
}

// 유튜브 페이지로부터 댓글 추출
function extractComments() {
    let comments = [];
    const commentElements = document.querySelectorAll("#content-text");
    commentElements.forEach(element => {
        comments.push(element.innerText);
    });
    return comments;
}

// 서버로 댓글 전송 & 성희롱 댓글 받아오기
async function getTargetCommentsFromServer(comments) {
    try {
        const title = await extractTitle();

        const response = await fetch('http://localhost:8000/find_comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: title, comments: comments }),
        })
        const data = await response.json();
        return data.target_comments; // 서버로부터 응답받는 type으로 정의
    } catch(e) {
        console.error("Error Finding Comments:", e)
        return []
    }
}

// targetComment blur 처리
function updateTargetComments(targetComments) {
    const all_comments = document.querySelectorAll('#content-text');

    all_comments.forEach((node) => {
        const comment = node.innerText;
        if (targetComments.includes(comment)) {
            const span = document.createElement("span");
            span.style.backgroundColor = "red"; // 배경색
            span.textContent = comment;
            node.innderHTML = '';
            node.appendChild(span);
            node.style.color = "white"; // 글자색색
        }
    })
}


