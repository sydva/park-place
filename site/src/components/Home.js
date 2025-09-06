import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSessionContext } from 'supertokens-auth-react/recipe/session';
import { signOut } from 'supertokens-auth-react/recipe/session';

function Home() {
  const session = useSessionContext();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  const handleAuth = () => {
    navigate('/auth');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏠 Park Place</h1>
        <p>
          Your marketplace for overnight parking
        </p>
        
        <div style={{ margin: '20px 0' }}>
          {session.loading ? (
            <p>Loading...</p>
          ) : session.doesSessionExist ? (
            <div>
              <p style={{ marginBottom: '20px' }}>Welcome back!</p>
              <nav style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', justifyContent: 'center' }}>
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
                <button 
                  onClick={handleSignOut}
                  style={{ 
                    color: '#61dafb', 
                    backgroundColor: 'transparent',
                    fontSize: '18px',
                    padding: '10px 20px',
                    border: '2px solid #61dafb',
                    borderRadius: '5px',
                    cursor: 'pointer'
                  }}
                >
                  Sign Out
                </button>
              </nav>
            </div>
          ) : (
            <div>
              <p style={{ marginBottom: '20px' }}>Sign in to start using Park Place!</p>
              <button 
                onClick={handleAuth}
                style={{ 
                  color: '#61dafb', 
                  backgroundColor: 'transparent',
                  fontSize: '18px',
                  padding: '10px 20px',
                  border: '2px solid #61dafb',
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
              >
                Sign In / Sign Up
              </button>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default Home;