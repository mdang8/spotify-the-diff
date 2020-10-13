import React, { useState } from 'react';
import { Menu } from '@material-ui/core';
import { useEffect } from 'react';

function App() {
  const [playlists, setPlaylists] = useState([]);

  useEffect(() => {
    // sends request to server to fetch playlists from Spotify API
    fetch('/playlists', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({  })
    })
      .then(res => res.json())
      .then(data => {
        // TODO - extract playlist data and set playlists object
        console.log(data);
        setPlaylists(data);
      });
  });
  
  return (
    <div id="app">
      <Menu id="playlist-menu">
      </Menu>
    </div>
  );
}

export default App;
