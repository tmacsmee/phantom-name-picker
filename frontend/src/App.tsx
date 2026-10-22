import { useEffect, useState } from 'react';

export default function App() {
  const [ghostNames, setGhostNames] = useState<string[]>([]);

  useEffect(() => {
    async function fetchGhostNames() {
      const res = await fetch('/api/ghosts');
      const _ghostNames = await res.json();
      setGhostNames(_ghostNames);
    }

    fetchGhostNames();
  }, []);

  return (
    <ul>
      {ghostNames.map((ghostName) => (
        <li>{ghostName}</li>
      ))}
    </ul>
  );
}
