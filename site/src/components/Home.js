import React from 'react';
import { Link } from 'react-router-dom';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/clerk-react';
import './Home.css';

function Home() {
  return (
    <div className="home">
      <div className="home-hero">
        <div className="home-topbar">
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>

        <h1 className="home-title">Park Place</h1>
        <p className="home-tagline">Yes in my driveway.</p>
        <p className="home-tagline">Your marketplace for overnight parking.</p>

        <SignedIn>
          <nav className="home-actions">
            <Link to="/map" className="btn-primary">View Map</Link>
            <Link to="/add-parking-space" className="btn-outline">Add Parking Space</Link>
            <Link to="/report-license-plate" className="btn-outline">Report License Plate</Link>
          </nav>
        </SignedIn>

        <SignedOut>
          <div className="home-actions">
            <SignInButton mode="modal">
              <button className="btn-primary">Get Started</button>
            </SignInButton>
            <Link to="/browse" className="btn-outline">Browse without signing in</Link>
          </div>
          <p className="home-note">Sign in to explore nearby spaces and list your own.</p>
        </SignedOut>
      </div>
    </div>
  );
}

export default Home;