# PyanoO

A small **Python 3 client–server chat system** I built around **2019**, when I was **15**. I had only been programming for about **two years**, mostly on my own time while going through **regular school**—not a coding-focused curriculum. This repo is here as a **historical snapshot** of that period: what I was trying to build, how I structured it, and what I did not yet know.

## Context (why this exists on my portfolio)

This is not a flagship product or a reference architecture. It is proof that I was already experimenting with **networking, concurrency, persistence, and “security-ish” features** before formal training or a job. The code reflects a teenager learning by doing: ambitious in scope, uneven in execution, and very much **“Proto1”** in spirit (that is literally the version string in the shared constants).

## What it is

- A **TCP socket server** (`server.py`) that accepts multiple clients on threads, with basic config, logging, and on-disk data under `PyanoO_Server_Data/` (users, message logs, server logs).
- A **Tkinter desktop client** (`client.py`) with a dark-themed connect screen and chat window, using **Pillow** for icons.
- A **custom wire protocol**: JSON message objects (sender, receiver, content, type, timestamp), a `PYA_`-prefixed handshake, and optional **AES (CFB)** encryption of payloads via **pycryptodome** when client and server share a key.
- **Users and passwords** stored as JSON files, password hashing helpers, **roles/permissions**, and server-side **commands** (e.g. list users, poke, kick, change password)—the kind of feature creep that felt exciting at 15.
- Shared modules split into `PyanoO_Client_Core`, `PyanoO_Server_Core`, and `PyanoO_Shared_Core`, which was my attempt at a “real” project layout before I knew standard packaging practices.

## What it is not

- **Not production-ready chat software.** No TLS, no modern auth story, no federation, no mobile/web clients, no ops story.
- **Not vetted cryptography.** Keys are derived and used in ways I would not ship today; treat encryption here as “obfuscation and learning,” not a security guarantee.
- **Not maintained.** Dependencies and Python versions have moved on; I have not hardening-passed this for 2026 environments.
- **Not representative of my current engineering bar.** It is representative of **early curiosity and persistence**.

## Limitations (honest list)

These are features of the artifact, not excuses—but they matter if you are browsing the code:

- **Security**: shared symmetric keys, custom crypto helpers, no threat model, no audit—fine for a LAN experiment, wrong for the internet.
- **Protocol design**: ad hoc JSON over TCP; no versioning strategy beyond a greeting blob; error handling and abuse resistance are minimal (strike counters exist, but this is not hardened).
- **Concurrency**: threading everywhere; race-prone patterns and in-memory structures that would not scale.
- **Code quality**: inconsistent style, duplicated logic, sharp edges in validators and crypto (including bugs I likely never noticed at the time).
- **UX**: desktop-only Tkinter; connect flow is functional, not polished.
- **Incomplete ideas**: the `notes` file is a scratchpad of todos I never finished—login messaging, IDs in the UI, and similar.

If you are evaluating **current** skills, look at recent work. If you are evaluating **trajectory**, this shows a 15-year-old trying to build a whole stack from scratch with documentation only from the internet and trial and error.

## Running it (best effort)

Requirements are minimal (`requirements.txt`: Pillow, pycryptodome). From the repo root:

```bash
pip install -r requirements.txt
./run_server.sh    # terminal 1
./run_client.sh    # terminal 2 — use the GUI to connect to host/port/key/user
```

On Windows, `start-server.bat` exists for the server side. You may need to set `PYTHONPATH` to the repo root if you launch modules differently (the shell scripts do this for you).

Expect to configure server constants under `PyanoO_Server_Core/constants.py` and to treat any shared **crypto key** as a shared secret for local testing only.

## License

No license file was added when I was 15. If you want to reuse anything, don't, it's not worth it lol.

---

*PyanoO — an old chat system from when I was 15, built because I wanted to see if I could.*
