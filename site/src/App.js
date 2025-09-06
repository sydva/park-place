import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SuperTokens, { SuperTokensWrapper } from 'supertokens-auth-react';
import { getSuperTokensRoutesForReactRouterDom } from 'supertokens-auth-react/ui';
import { SessionAuth } from 'supertokens-auth-react/recipe/session';
import EmailPassword from 'supertokens-auth-react/recipe/emailpassword';
import { EmailPasswordPreBuiltUI } from 'supertokens-auth-react/recipe/emailpassword/prebuiltui';
import Session from 'supertokens-auth-react/recipe/session';
import './App.css';
import Home from './components/Home';
import Map from './components/Map';
import ReportLicensePlate from './components/ReportLicensePlate';
import AddParkingSpace from './components/AddParkingSpace';

// Initialize SuperTokens
SuperTokens.init({
  appInfo: {
    appName: "Park Place",
    apiDomain: "http://localhost:8000",
    websiteDomain: "http://localhost:3000",
    apiBasePath: "/auth",
    websiteBasePath: "/auth"
  },
  recipeList: [
    EmailPassword.init(),
    Session.init()
  ]
});

function App() {
  return (
    <SuperTokensWrapper>
      <Router>
        <Routes>
          {/* SuperTokens auth routes */}
          {getSuperTokensRoutesForReactRouterDom(require("react-router-dom"), [EmailPasswordPreBuiltUI])}
          
          {/* Public routes */}
          <Route path="/" element={<Home />} />
          
          {/* Protected routes */}
          <Route path="/map" element={
            <SessionAuth>
              <Map />
            </SessionAuth>
          } />
          <Route path="/report-license-plate" element={
            <SessionAuth>
              <ReportLicensePlate />
            </SessionAuth>
          } />
          <Route path="/add-parking-space" element={
            <SessionAuth>
              <AddParkingSpace />
            </SessionAuth>
          } />
        </Routes>
      </Router>
    </SuperTokensWrapper>
  );
}

export default App;