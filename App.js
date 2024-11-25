import React from 'react';
import Header from './components/Header';
import ChatBox from './components/ChatBox';
import UploadButton from './components/UploadButton';
import './App.css';

const App = () => {
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    console.log(`File uploaded: ${file.name}`);
  };

  return (
    <div className="container">
      <Header />
      <ChatBox />
      <UploadButton onUpload={handleFileUpload} />
    </div>
  );
};

export default App;
