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
      <h3>Enter Your API Key</h3>
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
    </div>
  );
};

export default ApiInput;