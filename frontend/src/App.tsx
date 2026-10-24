import { type SubmitEvent, useEffect, useState } from 'react';

export default function App() {
  const [ghostNames, setGhostNames] = useState<string[]>([]);
  const [userId, setUserId] = useState<string>();
  const [csrfToken, setCsrfToken] = useState<string>();

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
    async function fetchCsrfToken() {
      const res = await fetch('/api/csrf');
      if (!res.ok) {
        return;
      }

      const csrfData = await res.json();
      setCsrfToken(csrfData.token);
    }

    fetchCsrfToken();
  }, []);

  useEffect(() => {
    async function fetchGhostNames() {
      const res = await fetch('/api/ghosts');
      const _ghostNames = await res.json();
      setGhostNames(_ghostNames);
    }

    fetchGhostNames();
  }, []);

  return (
    <div className="p-5">
      <main className="flex flex-col items-center">
        {userId ? (
          <NameForm
            availableNames={ghostNames}
            csrfToken={csrfToken}
            userId={userId}
          />
        ) : (
          <a href={'/api/login'} className="border p-2">
            {'Log in'}
          </a>
        )}
      </main>

      <section className="mt-8">
        <ul className="flex items-center flex-col">
          {ghostNames.map((ghostName) => (
            <li key={ghostName}>{ghostName}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function NameForm({
  availableNames,
  csrfToken,
  userId,
}: {
  availableNames: string[];
  csrfToken: string | undefined;
  userId: string;
}) {
  const [nameOptions, setNameOptions] = useState<string[]>([]);
  const [userName, setUserName] = useState<{ first: string; last: string }>();

  function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const firstName = String(formData.get('firstName') ?? '');
    const lastName = String(formData.get('lastName') ?? '');

    const names: string[] = [];
    while (names.length < 3) {
      const index = Math.floor(Math.random() * availableNames.length);
      const name = availableNames[index];
      if (names.includes(name)) {
        continue;
      }

      names.push(name);
    }

    setNameOptions(names);
    setUserName({ first: firstName, last: lastName });
  }

  async function handleOptionClick(option: string) {
    const key = option.toLowerCase().replace(' ', '_');

    await fetch(`/api/ghost/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken ?? '',
      },
      body: JSON.stringify({ ghostName: key }),
    });
  }

  return (
    <>
      <form className="flex flex-col gap-y-4" onSubmit={handleSubmit}>
        <div className="flex flex-col">
          <label htmlFor="firstName">First name</label>
          <input
            id="firstName"
            name="firstName"
            type="text"
            required
            maxLength={32}
            className="border"
          />
        </div>

        <div className="flex flex-col">
          <label htmlFor="lastName">Last name</label>
          <input
            id="lastName"
            name="lastName"
            type="text"
            required
            maxLength={32}
            className="border"
          />
        </div>

        <button type="submit" className="border p-2">
          Generate ghost names
        </button>
      </form>

      <ul className="flex gap-x-8">
        {nameOptions.map((option) => (
          <li key={option}>
            <button onClick={() => handleOptionClick(option)}>
              {userName?.first} "{option}" {userName?.last}
            </button>
          </li>
        ))}
      </ul>
    </>
  );
}
