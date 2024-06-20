// content.js

// debounce
// ex. debounce(() => void, 300)
function debounce(func, timeout = 5000) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => {
            func.apply(this, args);
        }, timeout);
    };
}

let ori_comments = [];

async function handleScrollEvent(e) {
    // 스크롤 됐을 때 이벤트 발생
    const new_comments = extractComments();

    if (ori_comments.length < new_comments.length) {
        // new comments which need to be sent
        // 기존 댓글과 비교해서 새롭게 추가된 댓글만 추출
        const comments_which_need_to_be_checked = new_comments.filter((_, index) => index > ori_comments.length - 1);
        const targetComments = await getTargetCommentsFromServer(comments_which_need_to_be_checked);
        //console.log(targetComments);
        updateTargetComment(targetComments);
        ori_comments = new_comments;
    }
}

window.addEventListener("scroll", debounce(handleScrollEvent, 1000))


// Function to extract comments from the page
function extractComments() {
    let comments = [];
    const commentElements = document.querySelectorAll('#content-text');
    commentElements.forEach(element => {
        comments.push(element.innerText);
    });
    return comments;
}

function extractTitle() {
    const titleElement = document.querySelector('meta[name="title"]').getAttribute('content');
    return titleElement;
}

// Function to send comments to the server
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
        return data.target_comment;
    } catch (e) {
        console.error("Error Finding Comments:", e)
        return []
    }
}

// targetComment를 업데이트하는 함수
function updateTargetComment(targetComments) {
    const all_comments = document.querySelectorAll('#content-text');

    all_comments.forEach((node) => {
        const comment = node.innerText
        if(targetComments.includes(comment)) {
            const span = document.createElement("span");
            span.style.backgroundColor = "red" // 배경색
            span.textContent = comment;
            node.innerHTML = '';
            node.appendChild(span);
            node.style.color = 'white'; // 글자색
        }
    })
}