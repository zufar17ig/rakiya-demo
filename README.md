# Rakiya

A local-first, adults-only short-term work marketplace for a Gampaha pilot. Founder and Product Lead: **Zufar Illyas**.

## Native phone app

The `mobile/` directory contains a React Native / Expo app targeting Android and iOS. It uses native controls and a separate bearer-authenticated API, with encrypted device session storage and opt-in foreground location. Start with the founder's Samsung A56 using Expo Go; see [the mobile instructions](mobile/README.md). A standalone APK/IPA has not been built or signed. `Start phone backend.cmd` deliberately starts a private-LAN test backend on port 8001; `Start mobile app.cmd` serves the native preview QR. These require a trusted Wi-Fi network and the PC to stay running. They do not purchase hosting, enable billing, or publish to app stores.

## Status

Working local prototype, **not publicly launched**. This build uses Django 5.2 and SQLite to make the main journey testable without cloud accounts or paid messaging. The original `Rakiya.html` is preserved as a historical pitch-page reference; its claims do not establish that features or adoption existed. Firebase and Twilio are not connected.

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_examples
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000. After one-time setup, double-click `Start Rakiya.cmd` in Windows File Explorer. It runs migrations, refreshes fictional examples, starts the server, and opens your default browser only after the app responds. Keep its window open while using Rakiya; closing it stops the app. A localhost link alone cannot start the app, and an agent's temporary test server may not be reachable from your normal browser. No global installations, Firebase billing, or Twilio credits are needed.

## Try the main journey

1. Create an employer account using a **test** +94 phone number, a strong password of at least 10 characters, and an adult birth date. SMS is not sent and the number is explicitly unverified.
2. Post a job for **today** within 20 km of Gampaha; specify the workplace coordinates. Each listing currently hires one person. No fee is charged.
3. Sign out and register a worker in another account. Browse, search, optionally grant browser location access, then apply to the test job. Fictional example listings cannot receive applications.
4. Sign in as the employer, open My activity, and accept. Only the matched parties can now see the other party's contact number. Other pending applicants are declined.
5. Confirm work and rate the worker. The worker then confirms all promised compensation and rates the employer. The application and job close only after both steps.
6. Test hold, decline, withdrawal, cancellation, and private reports for payment, safety, cancellation, or no-shows. Confirmation is a party's statement, **not independent proof of payment or identity**.

## Admin

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Use `/admin/` with that separate staff account. No default admin password exists. Review and resolve reports with a written resolution; reviews create an audit event. Do not distribute staff credentials. Personal test data and secrets stay in ignored local files.

## Tests

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
node --check static/app.js
```

Tests cover hiring/closure, private contacts, role restrictions, ownership, CSRF, adult registration, password hashing, login limits, geographic filtering, cancellations, reports, and admin access.

## Design and language

Light aqua `#D9EFF7`, periwinkle `#9BB8FC`, purple `#4741A6`, yellow `#F9CE69`. Original clay-like characters are drawn with CSS; no reference artwork is copied. English/Tamil interface dictionaries live in `static/app.js`. Sinhala can be added as another dictionary; Tamil needs native-speaker review before launch. User-written listings are not automatically translated. Optional Google Fonts have system fallbacks.

## Security and limitations

Django supplies hashed passwords, server-side sessions, CSRF validation, automatic template escaping, and staff permissions. API authorization is server-side; public listings never contain phone numbers. Login attempts are persistently limited by the immediate IP address. An initial local build deliberately uses password authentication rather than claiming that an unverified phone number is an identity. Age is self-declared and not verified.

The development server binds to loopback and is **not a production server**. Production settings require a separate environment secret and enable HTTPS redirect, secure cookies, and HSTS. Before a public pilot: select production hosting, back up the database, configure HTTPS and trusted hosts, add verified SMS authentication and recovery, email/contact support, abuse controls for signup and posting, monitoring, consent/privacy/retention policies, moderation procedures, and test production deployment. Integrate Firebase only if a deliberate migration is worthwhile; do not add open Firestore rules or store authentication in localStorage. No Firebase rules are deployed by this build.

Direct GPS distance is straight-line Haversine distance, not travel distance. Coordinates are explicit; no geocoding API is called. Overnight and multi-worker shifts, uploads, in-app messaging, automated notifications, payment processing, and full WhatsApp integration remain future work. Admin resolution records outcomes but does not automatically adjudicate employment disputes. There is no blanket theft ban without review.

## Ownership and contributor credit

Zufar Illyas identifies himself as the sole founder/product creator. Report/presentation assistance was provided by Fathima Hilmy, Ashini Wageesha, Chandhupa Chamupathi, and Isuru Sathsara; exact contribution wording awaits confirmation. No cofounder or continuing operational role is implied. Ownership agreements and permission for report material must be clarified before publication or licensing. **No open-source license has been selected.** Public visibility is not itself an open-source license.

## Claude application evidence

See `docs/CLAUDE_APPLICATION.md`. Do not claim users, contributors, downloads, production readiness, or verified hiring outcomes based on demo data or tests. This build does not establish program eligibility.
