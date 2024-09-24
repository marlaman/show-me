// src/components/ui/Input.js

import React from 'react';

export function Input({ className, ...props }) {
  return (
    <input
      className={`border rounded-lg py-2 px-4 ${className}`}
      {...props}
    />
  );
}
