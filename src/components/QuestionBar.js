import React, { useState } from 'react';

function QuestionBar({ onSubmit }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={input} onChange={e => setInput(e.target.value)} />
      <button type="submit">Ask</button>
    </form>
  );
}

export default QuestionBar;
