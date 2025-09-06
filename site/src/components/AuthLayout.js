import React from 'react';
import './AuthLayout.css';

const AuthLayout = ({ children }) => {
  return (
    <div className="auth-layout">
      <div className="auth-illustration" aria-hidden="true">
        <div className="road" />
        <div className="parking-lot">
          <div className="spot" />
          <div className="spot" />
          <div className="spot" />
          <div className="spot" />
          <div className="spot" />
          <div className="spot" />
        </div>
        <div className="car" />
      </div>
      <div className="auth-content">
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
