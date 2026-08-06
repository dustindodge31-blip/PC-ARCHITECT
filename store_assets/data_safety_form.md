# Play Console — Data Safety Form Answers

Reference for filling out App content → Data safety in Play Console.

## Does your app collect or share any of the required user data types?
**Yes**

## Data types collected

### Personal info → Email address
- Collected: Yes
- Shared with third parties: No (sent to Supabase, our backend provider, not shared/sold onward)
- Purpose: Account management (sign up / sign in for AI Architect, publishing, favoriting, and reporting)
- Optional or required: Optional to install/use the app overall (browsing the community feed and local builds don't need one), but required to use AI Architect or publish/favorite/report a build

### App activity → Other user-generated content
- Collected: Yes
- What: Build names, selected parts, and reasoning text for builds a user chooses to publish; AI Architect prompts (forwarded to our server function, not stored by us beyond displaying the result and enforcing the daily usage cap)
- Shared with third parties: Yes — AI Architect prompts are forwarded to Google's Gemini API via our own server function
- Purpose: App functionality (the community feed, AI Architect)
- Optional or required: Optional

### App info and performance → Crash logs
- Collected: Yes
- Shared with third parties: Yes (Sentry)
- Purpose: App functionality (fixing bugs) — not linked to user identity
- Optional or required: Required (automatic, not user-initiated)

## Data NOT collected
- Location
- Contacts
- Photos/videos
- Financial info
- Health/fitness
- Messages
- Web browsing history
- Device/other IDs used for advertising
- Precise or approximate location

## Security practices
- Data is encrypted in transit: Yes (HTTPS to Supabase and Google's Gemini API)
- Users can request data deletion: Yes (contact developer — mention email/method you want to use)

## Third parties data is sent to
- **Supabase** (auth + database + our own gemini-proxy server function) — email/password for account creation, published build content, AI Architect prompts en route to Gemini, and usage-limit bookkeeping
- **Google Gemini API** — the free-text prompt a user types into AI Architect (relayed via our Supabase server function, which holds the API key so it never ships in the app), to generate a build suggestion. Not stored by PC Architect beyond displaying the result.
- **Sentry** — crash reports (stack trace, device/OS, app version) if the app hits an unexpected error. Not linked to email/account.

## Notes
- No ads SDK, no analytics/marketing-tracking SDK.
- Sentry crash reporting was added after initial launch — this form was updated to match.
- If anything else changes, this form and the privacy policy (docs/privacy-policy.html) both need
  updating to match — Play Console checks for consistency between the two.
