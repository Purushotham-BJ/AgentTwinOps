# OAuth Authentication

AgentTwinOps supports the existing email/password authentication and optional
Google and GitHub OAuth authorization-code flows.

## Configuration

Set these backend variables only when enabling a provider:

```env
FRONTEND_URL=https://ops.example.com
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://api.example.com/api/v1/auth/oauth/google/callback
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_REDIRECT_URI=https://api.example.com/api/v1/auth/oauth/github/callback
```

Provider credentials are never sent to the browser. Google requests only
`openid email profile`; GitHub uses `read:user user:email`. Provider emails must
be verified (GitHub requires a verified primary email).

Email/password registration requires 8-128 characters, at least one uppercase
letter, one lowercase letter, one number, and one supported special character.
The frontend shows these requirements, but the backend enforces them
independently. Existing password login and OAuth-only accounts are not subject
to this registration policy.

## Flow and safety

`/api/v1/auth/oauth/{provider}/login` starts sign-in and
`/api/v1/auth/oauth/{provider}/callback` exchanges the code server-side. The
callback validates a signed, expiring state value and creates or links a
`user_auth_accounts` identity using the provider subject. Existing users are
linked only by a verified provider email; provider subjects are unique and
cannot be linked to a second AgentTwinOps user.

The callback redirects with the AgentTwinOps JWT in a URL fragment. Fragments
are not sent in HTTP requests, and the frontend immediately stores the token
and removes the fragment. Provider access tokens are never exposed.

Authenticated users can start a linking flow at
`/api/v1/auth/oauth/{provider}/start`; connected identities are listed at
`/api/v1/auth/oauth/providers`.

If provider configuration is missing, email/password login remains available
and the provider start endpoint returns `503`. Apply the OAuth Alembic
migration before enabling a provider.
