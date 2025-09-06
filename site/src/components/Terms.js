import React from 'react';

const Terms = () => (
  <div style={{ maxWidth: 800, margin: '40px auto', padding: '0 16px', lineHeight: 1.7 }}>
    <h1>Terms of Service</h1>
    <p>Last updated: {new Date().toLocaleDateString()}</p>
    <p>Welcome to Park Place. By accessing or using our services, you agree to these Terms of Service. If you do not agree, please do not use the service.</p>
    <h2>Use of Service</h2>
    <p>You agree to use the service in compliance with applicable laws and not to misuse the platform, including but not limited to fraudulent activity, harassment, or interfering with others' use.</p>
    <h2>Accounts</h2>
    <p>You are responsible for maintaining the confidentiality of your account credentials and for all activities under your account.</p>
    <h2>Content</h2>
    <p>Content you submit may be used to improve the service. Do not submit unlawful, infringing, or inappropriate content.</p>
    <h2>Payments</h2>
    <p>Payment processing may be handled by third parties. All fees are non-refundable unless required by law.</p>
    <h2>Disclaimers</h2>
    <p>The service is provided "as is" without warranties of any kind. We do not guarantee availability, accuracy, or suitability for any purpose.</p>
    <h2>Limitation of Liability</h2>
    <p>To the maximum extent permitted by law, Park Place shall not be liable for any indirect, incidental, or consequential damages arising from use of the service.</p>
    <h2>Termination</h2>
    <p>We may suspend or terminate access to the service at any time for any reason.</p>
    <h2>Changes</h2>
    <p>We may update these Terms from time to time. Continued use constitutes acceptance of the updated Terms.</p>
    <p>If you have questions, contact us at support@parkplace.example.</p>
  </div>
);

export default Terms;
