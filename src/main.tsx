import React from 'react';
import { createRoot } from 'react-dom/client';
import PlayerApp from './player-app';
createRoot(document.getElementById('root')!).render(<React.StrictMode><PlayerApp/></React.StrictMode>);
