import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to React</h1>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <nav style={{ margin: '20px 0' }}>
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
        </nav>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default Home;