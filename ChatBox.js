import React, { useState } from 'react';
import './ChatBox.css';

const ChatBox = () => {
  const [message, setMessage] = useState('');
  const [chatMessages, setChatMessages] = useState([]);

  const handleSendMessage = () => {
    if (message) {
      setChatMessages([
        ...chatMessages,
        { user: 'S', text: message, id: Date.now() },
        { user: 'AI', text: 'Our own Large Language Model (LLM) is a type of AI...', id: Date.now() + 1 },
      ]);
      setMessage('');
    }
  };

  return (
    <div className="chat-box">
      <div className="message-area">
        {chatMessages.map((msg) => (
          <div key={msg.id} className={`message ${msg.user === 'S' ? 'sender' : 'receiver'}`}>
            <p className="message-text">{msg.text}</p>
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Send a message..."
          className="message-input"
        />
        <button onClick={handleSendMessage} className="send-btn">
          &#8594;
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
