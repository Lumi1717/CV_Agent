import { useState, useRef, useEffect } from 'react'; // Add useRef and useEffect

const ChatWindow = ({ apiKey }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const chatContainerRef = useRef(null); // Create a ref for the chat container

  // Sample questions
  const sampleQuestions = [
    'How many years of experience does Ahlam have?',
    'How many companies did Ahlam work for?',
    'Where does Ahlam work right now?',
    'Coffee or Karak?',
  ];

  // Scroll to the bottom of the chat container whenever messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]); // Trigger this effect whenever messages change

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!apiKey) {
      alert('Please add an API key to continue.');
      return;
    }

    const userMessage = { text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: input, apiKey}),
      });

      const data = await response.json();
      const botMessage = { text: data.answer, sender: 'bot' };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error fetching response:', error);
      setMessages((prev) => [...prev, { text: 'Error: Unable to fetch response.', sender: 'bot' }]);
    }

    setInput('');
  };

  // Handle click on sample question
  const handleSampleQuestionClick = (question) => {
    setInput(question); // Populate the input field with the question
  };

  return (
    <div className="chat-window">
      <div className="message-history" ref={chatContainerRef}> {/* Add ref here */}
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <strong>{msg.sender}:</strong> {msg.text}
          </div>
        ))}
      </div>

      {/* Sample questions section */}
      <div className="sample-questions">
        <h4>Sample Questions</h4>
        <div className="questions-list">
          {sampleQuestions.map((question, index) => (
            <div
              key={index}
              className="question"
              onClick={() => handleSampleQuestionClick(question)}
            >
              {question}
            </div>
          ))}
        </div>
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="input-area">
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default ChatWindow;