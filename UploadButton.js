import React from 'react';

const UploadButton = ({ onUpload }) => {
  return (
    <button className="upload-btn">
      <input type="file" accept=".pdf" onChange={onUpload} hidden />
      Upload PDF
    </button>
  );
};

export default UploadButton;
