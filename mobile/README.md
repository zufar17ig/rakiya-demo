# Rakiya native Android + iPhone app

React Native / Expo SDK 57. Uses native controls and the existing Django backend; it is not a WebView wrapper. Android-first physical testing is intended for the founder's Samsung A56. The same source targets iOS. No store submission, paid build, cloud deployment or developer enrollment has been made.

## Free physical-device preview

1. Install the official **Expo Go** app on the Anrdoid from Google Play. Do not pay for Expo cloud services.
2. Connect the PC and phone to the same **trusted private Wi-Fi**. Avoid guest Wi-Fi/client isolation; temporarily disconnect a VPN if it prevents local connectivity.
3. From the repository, run **Start phone backend.cmd**. It binds only to a private PC address on port 8001 and prints `PHONE SERVER ADDRESS`. Keep the window open. Use test credentials only on this HTTP development connection.
4. Run **Start mobile app.cmd**, keep that window open, and scan its QR code from Expo Go.
5. In the Rakiya app's server screen enter the printed address, e.g. `http://192.168.1.10:8001`. Do not enter `127.0.0.1`: on a phone that means the phone itself. If multiple network adapters exist, set `RAKIYA_LAN_HOST` to the PC's Wi-Fi IPv4 address before launching the backend.
6. Browse examples, create an adult test employer account, post a job for today, and use a separate worker account to apply. Accept, confirm work, then confirm compensation. Pull down to refresh. Use the activity tab for cancellations and disputes, and the profile tab to edit account details. The language toggle switches English and Tamil (translation review pending).

If Windows asks about local network access, allow only on your trusted private network. The launcher does not modify firewall rules. Native app and backend must both remain available. No mobile data/cloud fallback exists. This is not an offline marketplace.

Expo Go runs native Rakiya code inside its preview app. It is **not yet a standalone Rakiya APK or signed iPhone app**. iPhone Expo Go testing is possible from this same project, subject to compatible Expo Go availability.

## Developer setup / validation

```powershell
cd mobile
npm ci
npx tsc --noEmit
npx expo export --platform android --platform ios --output-dir dist
npm start -- --lan
```

The exported bundles validate JavaScript/asset packaging for both platforms, not native device behavior or signing. A real A56/iPhone has not been tested by the agent. Location is foreground-only and requested on demand. All examples remain fictional. Native forms and most chrome share the web English/Tamil dictionaries; some setup/error prompts remain English. Sinhala can be added through another dictionary.

## Session security

`/mobile-api/` accepts explicit opaque bearer session keys. Native requests ignore browser-cookie identity; the browser API retains CSRF protection. Tokens are stored in Expo SecureStore, not AsyncStorage or source code. Server-side logout revokes the token. The connection screen accepts HTTPS; private HTTP is allowed only in development (`__DEV__`). Production requires a hosted HTTPS backend. Switching server clears the local token. Do not distribute local HTTP builds to real customers. SMS verification and account recovery remain unconnected.

## Standalone builds later

Prepared `eas.json` profiles describe Android APK preview and production builds. EAS commands can create accounts/use cloud quotas, so none have been run. Local Android building needs a complete JDK/Android build toolchain. iOS local building needs macOS/Xcode; device/store distribution needs Apple's applicable signing setup. Store registrations or paid services require the founder's approval. Configure a production HTTPS backend and test transport settings, keyboard/safe areas, permission handling, session expiry, and real device accessibility before release. No APK/IPA is claimed as delivered by this source project.

Publishing the source does not make it open source until a license is deliberately selected. The app does not establish Claude-program eligibility.

Third-party notice: EXPO_TEMPLATE_LICENSE.txt applies to Expo starter material; it does not select a license for Rakiya's original code.
