import React from 'react';

const Privacy = () => (
  <div style={{ maxWidth: 800, margin: '40px auto', padding: '0 16px', lineHeight: 1.7 }}>
    <h1>Privacy Policy</h1>
    <p>Last updated: {new Date().toLocaleDateString()}</p>
    <p>This Privacy Policy describes how Park Place collects, uses, and shares information when you use our services.</p>
    <h2>Information We Collect</h2>
    <p>We may collect information you provide (e.g., email, profile details), location data for map features, and usage data to improve our services.</p>
    <h2>How We Use Information</h2>
    <p>We use information to operate, maintain, and improve the service, provide customer support, and comply with legal obligations.</p>
    <h2>Sharing</h2>
    <p>We may share information with service providers (e.g., payment processors) under appropriate safeguards. We do not sell personal information.</p>
    <h2>Security</h2>
    <p>We implement measures to protect your information; however, no method of transmission or storage is 100% secure.</p>
    <h2>Your Choices</h2>
    <p>You may access, update, or delete certain information in your account. You may also control location permissions in your device settings.</p>
    <h2>Children</h2>
    <p>Our services are not directed to children under 13. We do not knowingly collect information from children.</p>
    <h2>Changes</h2>
    <p>We may update this Policy from time to time. Continued use constitutes acceptance of the updated Policy.</p>
    <p>Questions? Contact support@parkplace.example.</p>
  </div>
);

export default Privacy;
