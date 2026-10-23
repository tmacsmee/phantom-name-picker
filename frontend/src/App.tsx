import { type SubmitEvent, useEffect, useState } from 'react';

export default function App() {
  const [ghostNames, setGhostNames] = useState<string[]>([]);
  const [nameOptions, setNameOptions] = useState<string[]>([]);
  const [userId, setUserId] = useState<string>();

  useEffect(() => {
    async function fetchUser() {
      const res = await fetch('/api/user');
      if (!res.ok) {
        return;
      }

      const userData = await res.json();
      setUserId(userData.sub);
    }

    fetchUser();
  }, []);

  useEffect(() => {
    async function fetchGhostNames() {
      const res = await fetch('/api/ghosts');
      const _ghostNames = await res.json();
      setGhostNames(_ghostNames);
    }

    fetchGhostNames();
  }, []);

  function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    const names = [];
    for (let i = 0; i < 3; i++) {
      const index = Math.floor(Math.random() * ghostNames.length);
      names.push(ghostNames[index]);
    }

    setNameOptions(names);
  }

  return (
    <>
      <main className="flex flex-col items-center">
        <a href={userId ? '/api/logout' : '/api/login'} className="border p-2">
          {userId || 'Log in'}
        </a>

        <form className="flex flex-col gap-y-4" onSubmit={handleSubmit}>
          <div className="flex flex-col">
            <label htmlFor="firstName">First name</label>
            <input id="firstName" type="text" className="border" />
          </div>

          <div className="flex flex-col">
            <label htmlFor="lastName">Last name</label>
            <input id="lastName" type="text" className="border" />
          </div>

          <button type="submit" className="border p-2">
            Generate ghost names
          </button>
        </form>

        <ul className="flex gap-x-8">
          {nameOptions.map((option) => (
            <li key={option}>
              <button>John "{option}" Doe</button>
            </li>
          ))}
        </ul>
      </main>

      <section className="mt-8">
        <ul className="flex items-center flex-col">
          {ghostNames.map((ghostName) => (
            <li key={ghostName}>{ghostName}</li>
          ))}
        </ul>
      </section>
    </>
  );
}
