import React from 'react';
import { Link } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';

function Home() {
  return (
    <div className="App">
      <header className="App-header">
        <div style={{ position: 'absolute', top: 20, right: 20 }}>
          <SignedOut>
            <SignInButton />
          </SignedOut>
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>
        
        <h1>🏠 Park Place</h1>
        <p>
          Your marketplace for overnight parking
        </p>
        
        <SignedIn>
          <nav style={{ margin: '20px 0', display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
            <Link 
              to="/map" 
              style={{ 
                color: '#61dafb', 
                textDecoration: 'none',
                fontSize: '18px',
                padding: '10px 20px',
                border: '2px solid #61dafb',
                borderRadius: '5px',
                display: 'inline-block'
              }}
            >
              View Map
            </Link>
            <Link 
              to="/add-parking-space" 
              style={{ 
                color: '#61dafb', 
                textDecoration: 'none',
                fontSize: '18px',
                padding: '10px 20px',
                border: '2px solid #61dafb',
                borderRadius: '5px',
                display: 'inline-block'
              }}
            >
              Add Parking Space
            </Link>
            <Link 
              to="/report-license-plate" 
              style={{ 
                color: '#61dafb', 
                textDecoration: 'none',
                fontSize: '18px',
                padding: '10px 20px',
                border: '2px solid #61dafb',
                borderRadius: '5px',
                display: 'inline-block'
              }}
            >
              Report License Plate
            </Link>
          </nav>
        </SignedIn>
        
        <SignedOut>
          <p style={{ marginTop: '40px' }}>
            Please sign in to access Park Place features.
          </p>
        </SignedOut>
      </header>
    </div>
  );
}

export default Home;