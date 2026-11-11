# Local build verification — 2026-11-11

## Passed locally

- 24 Django tests covering the hiring journey and access/security boundaries.
- Django system check: no issues.
- JavaScript syntax check.
- Headless Edge browser check: six explicitly fictional examples, category filtering, 390px mobile width with no horizontal overflow, Tamil toggle, adult account registration, employer job posting, worker application, contact hidden before acceptance, contact revealed to the accepted match, employer confirmation, worker compensation confirmation, completed record, and no JavaScript runtime errors.
- Desktop and mobile landing screenshots visually inspected. Test screenshots live under ignored `test-results/`.

The browser check creates clearly named Browser QA test accounts and local job records. It uses a temporary loopback server at port 8016 and closes it after the test. Set PLAYWRIGHT_MODULE to a local Playwright module path if needed; a locally installed Microsoft Edge is required. This is an optional developer check, not part of normal startup.

## Operational boundaries

- Local preview only; no public deployment, billing changes, or application submission.
- Source was cloned from the public repository. Initial connector write tools were unavailable; local Git authentication was subsequently established through Git Credential Manager. Development changes are prepared on the dedicated codex/rakiya-app review branch; main is preserved.
- CI workflow is prepared but has not run on GitHub.
- No license selected.
- No Firebase or Twilio configuration was read or changed.
- Phone numbers are unverified; age is self-declared. Password authentication is real, not simulated SMS authentication.
- WhatsApp automation, phone OTP and recovery, hosted notifications, and payment processing are not connected or simulated as if delivered.
- Tamil interface is implemented, but translation quality needs a native-speaker review. Dynamic listings and framework-admin screens are not fully localized.
- Original procedural CSS character illustrations provide the sculpted 3D visual style; they are not downloadable 3D models.
- Public pilot still requires deployment work, operations/privacy policies, stronger verification and account recovery, monitoring, and review of local employment requirements.

This verification is evidence of local software behavior, not user adoption, employment outcomes, ecosystem impact, or eligibility for any subscription program.

## Native mobile addition — 2026-11-11

- React Native / Expo SDK 57 source targets Android and iOS, with shared English/Tamil dictionaries and native job, account, application, completion, report and profile controls.
- TypeScript check passed. Android and iOS Hermes JavaScript bundle exports passed. These are JavaScript bundles, not signed APK/IPA packages.
- Five new mobile API tests passed: explicit bearer sessions, revocation, cookie isolation, preserved browser CSRF checks, invalid sessions, and adult registration.
- Full regression run passed: 29 tests, including the original web hiring/privacy tests and the five native session tests; Django system checks reported no issues.
- No USB test device was attached. No physical Samsung A56 or iPhone behavior has been verified. iOS signing/store submission and standalone Android packaging remain outstanding.
- Native sessions use Django's expiring/revocable database sessions and Expo SecureStore. Local HTTP is permitted by the app only during development against private addresses; use only test credentials. Production requires HTTPS and a separately reviewed deployment.
- Final SDK 57 dependency audit reports 12 findings (9 moderate, 3 high), including the router's query-string/decode-uri-component dependency chain and build/lint glob/minimatch chains. A compatible `npm audit fix` was attempted; the findings remain. Forced framework changes were not applied. These are release blockers tracked in this draft, not a claim of production readiness. Native builds must not be distributed to customers until the dependency chain is upgraded or patched and retested.
- The initial GitHub dry-run failed due to missing local credentials. A subsequent Git Credential Manager sign-in succeeded, and a dry-run confirmed write permission to the dedicated review branch. No broad GitHub permission settings were changed.

Dependency advisories: https://github.com/advisories/GHSA-3g3m-2fjr-6pw4 and https://github.com/advisories/GHSA-g3hv-75wg-m249 .

- Expo Router now owns main-screen navigation; TypeScript and ESLint checks pass without warnings.
