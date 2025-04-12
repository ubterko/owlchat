let isTyping = false;

let chat = null
let chatMessage = null;
let chatOwner = null;

const token = sessionStorage.getItem("token");
const authToken = token;

const socket = new WebSocket(`ws://localhost:8000/api/socket?raw_token=${token}`);
socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const _isTyping = data.message.split(':')[0] === 'false' ? false : true;
    const message = data.message.split(':')[1]
    const messageArea = document.getElementById('message-div');
    if (_isTyping) {
        chatMessage.textContent = message;
    } else {
        chatMessage = document.createElement('p');
        chatOwner = document.createElement('p');
        chat = document.createElement('div');
    // append new elements to dom
        messageArea.appendChild(chat);
        chat.setAttribute('class', data.user_token === authToken ? 'my-msg': '' )
        chat.appendChild(chatOwner);
        chat.appendChild(chatMessage);
    // update with new messages
        chatMessage.textContent = message;
        chatOwner.textContent = data.user_name;
    }
    
};

function sendInitialMessage(){
    const message = document.getElementById('msg');
    if (isTyping) {
        socket.send(`true:${message.value}`)
    } else {
        socket.send(`false:${message.value}`)
        isTyping = true;
    }
}

function sendChatMessage(){
    const message = document.getElementById('msg');
    const myMessage = document.getElementsByClassName('my-msg');
    for (let elem of myMessage) {
        elem.setAttribute('style','display: block;');
    }
    message.value = '';
    isTyping = false;
}

function signIn(){
    let input = document.getElementById('input');
    fetch('http://localhost:8000', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }, body: JSON.stringify({'username':input.value}) })
        .then(response => response.json())
        .then(response => {
            sessionStorage.setItem("token", response.token);
            // window.location.href="http://localhost:8000/chatroom";
            window.location.replace("http://localhost:8000/chatroom");
        }) 
};