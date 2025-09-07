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
        <div className="auth-header">
          <h1 className="brand">Park Place</h1>
          <p className="tagline">Yes in my driveway.</p>
        </div>
        <div className="auth-card">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
