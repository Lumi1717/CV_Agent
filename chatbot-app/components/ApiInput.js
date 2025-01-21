import { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';

const ApiInput = ({ onApiSubmit }) => {
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false); // State to toggle visibility

  const handleSubmit = (e) => {
    e.preventDefault();
    onApiSubmit(apiKey);
  };

  return (
    <div className="left-panel">
      <h3>Enter Your Gemini API Key</h3>
      <form onSubmit={handleSubmit}>
        <div style={{ position: 'relative', width: '100%' }}>
          <input
            type={showApiKey ? 'text' : 'password'} // Toggle between text and password
            placeholder="Your API Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            style={{ paddingRight: '2px', width: '100%' }} // Add padding for the eye icon
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            style={{
              position: 'absolute',
              right: '-160px',
              top: '40%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '0', // Remove default button padding
            }}
          >
            <FontAwesomeIcon icon={showApiKey ? faEyeSlash : faEye} /> {/* Eye icon */}
          </button>
        </div>
        <button type="submit">Save API Key</button>
      </form>
      <p style={{ marginTop: '10px', fontSize: '14px', color: '#E5E7EB' }}>
        Don't have an API key?{' '}
        <a
          href="https://aistudio.google.com/apikey"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#3B82F6', textDecoration: 'none' }}
        >
          Get your Gemini API key here
        </a>
        .
      </p>
    </div>
  );
};

export default ApiInput;