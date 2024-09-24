// src/components/ui/Card.js

import React from 'react';

export function Card({ className, children }) {
  return (
    <div className={`bg-white p-4 rounded-lg shadow ${className}`}>
      {children}
    </div>
  );
}
