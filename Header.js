import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <div className="header">
      <img src="/images/logo.png" alt="Logo" className="logo" />
      <button className="upload-btn">Upload PDF</button>
    </div>
  );
};

export default Header;
