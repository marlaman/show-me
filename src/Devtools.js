import React, { useState } from 'react';
import { Panel } from 'reactflow';
import ChangeLogger from './ChangeLogger';

export default function DevTools() {
  const [changeLoggerActive, setChangeLoggerActive] = useState(true);

  return (
    <div className="react-flow__devtools">
      <Panel position="top-left">
        <DevToolButton
          setActive={setChangeLoggerActive}
          active={changeLoggerActive}
          title="Toggle Change Logger"
        >
          Change Logger
        </DevToolButton>
      </Panel>
      {changeLoggerActive && <ChangeLogger />}
    </div>
  );
}

function DevToolButton({ active, setActive, children, ...rest }) {
  return (
    <button
      onClick={() => setActive((a) => !a)}
      className={active ? 'active' : ''}
      {...rest}
    >
      {children}
    </button>
  );
}
