import { useState } from 'react';
import ApiInput from '../components/ApiInput';
import ChatWindow from '../components/ChatWindow';

export default function Home() {
  const [apiKey, setApiKey] = useState('');

  return (
    <div className="app-container">
      <ApiInput onApiSubmit={setApiKey} />
      <ChatWindow apiKey={apiKey} />
    </div>
  );
}