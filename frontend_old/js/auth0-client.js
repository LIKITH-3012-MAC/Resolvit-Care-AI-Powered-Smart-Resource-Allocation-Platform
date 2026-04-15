/**
 * Auth0 SPA Integration — RESOLVIT
 * Handles Auth0 Universal Login, Google social connection, and token exchange.
 * 
 * Uses Auth0 SPA SDK loaded via CDN.
 * After Auth0 authenticates, we exchange the token for a local JWT via POST /auth/auth0-userinfo
 */

// ──── Auth0 Configuration ────
// These can be overridden via window.AUTH0_CONFIG before this script loads
const AUTH0_CONFIG = window.AUTH0_CONFIG || {
  domain:   'YOUR_AUTH0_DOMAIN.us.auth0.com',    // Replace with your Auth0 domain
  clientId: 'YOUR_AUTH0_CLIENT_ID',               // Replace with your Auth0 SPA Client ID
  audience: 'https://smartresource-api',           // Must match Auth0 API Identifier
  redirectUri: window.location.origin + '/callback.html',
  logoutUri:   window.location.origin + '/login.html',
};

const AUTH_BASE_URL = window.AUTH_BASE_URL || 'http://127.0.0.1:8000/auth';

let auth0Client = null;

/**
 * Initialize the Auth0 SPA client.
 * Call this on page load (DOMContentLoaded).
 */
async function initAuth0() {
  if (typeof createAuth0Client === 'undefined') {
    console.warn('Auth0 SPA SDK not loaded. Social login unavailable.');
    return null;
  }

  try {
    auth0Client = await createAuth0Client({
      domain:        AUTH0_CONFIG.domain,
      clientId:      AUTH0_CONFIG.clientId,
      authorizationParams: {
        redirect_uri: AUTH0_CONFIG.redirectUri,
        audience:     AUTH0_CONFIG.audience || undefined,
        scope:        'openid profile email',
      },
      cacheLocation: 'localstorage',
      useRefreshTokens: true,
    });
    console.log('✅ Auth0 client initialized');
    return auth0Client;
  } catch (err) {
    console.error('❌ Auth0 init failed:', err);
    return null;
  }
}

/**
 * Redirect to Auth0 Universal Login with Google pre-selected.
 */
async function loginWithGoogle() {
  if (!auth0Client) await initAuth0();
  if (!auth0Client) {
    showToast?.('Social login not available. Please use email login.', 'error');
    return;
  }

  try {
    await auth0Client.loginWithRedirect({
      authorizationParams: {
        connection: 'google-oauth2',
        redirect_uri: AUTH0_CONFIG.redirectUri,
      },
    });
  } catch (err) {
    console.error('Auth0 Google login error:', err);
    showToast?.('Google login failed. Please try again.', 'error');
  }
}

/**
 * Redirect to Auth0 Universal Login (all providers).
 */
async function loginWithAuth0() {
  if (!auth0Client) await initAuth0();
  if (!auth0Client) {
    showToast?.('Social login not available. Please use email login.', 'error');
    return;
  }

  try {
    await auth0Client.loginWithRedirect({
      authorizationParams: {
        redirect_uri: AUTH0_CONFIG.redirectUri,
      },
    });
  } catch (err) {
    console.error('Auth0 login error:', err);
    showToast?.('Login failed. Please try again.', 'error');
  }
}

/**
 * Handle the Auth0 redirect callback on /callback.html.
 * Extracts the Auth0 token, exchanges it for a local JWT, and redirects to dashboard.
 */
async function handleAuth0Callback() {
  if (!auth0Client) await initAuth0();
  if (!auth0Client) {
    console.error('Auth0 client not available');
    window.location.href = '/login.html?error=auth0_unavailable';
    return;
  }

  try {
    // Process the redirect
    const result = await auth0Client.handleRedirectCallback();
    console.log('Auth0 callback processed:', result);

    // Get the user profile and access token
    const user = await auth0Client.getUser();
    let accessToken = null;

    try {
      accessToken = await auth0Client.getTokenSilently();
    } catch (tokenErr) {
      console.warn('Could not get access token silently:', tokenErr);
    }

    console.log('Auth0 user:', user);

    // Exchange with our backend — try JWT endpoint first, fall back to userinfo
    let backendResponse;

    if (accessToken) {
      // Try the JWT verification endpoint
      try {
        backendResponse = await fetch(`${AUTH_BASE_URL}/auth0-callback`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: accessToken }),
        });
        if (!backendResponse.ok) throw new Error('JWT callback failed');
        backendResponse = await backendResponse.json();
      } catch (jwtErr) {
        console.warn('JWT callback failed, trying userinfo endpoint:', jwtErr);
        backendResponse = null;
      }
    }

    if (!backendResponse) {
      // Fallback: send user info directly
      backendResponse = await fetch(`${AUTH_BASE_URL}/auth0-userinfo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          access_token: accessToken || '',
          user_info: {
            sub:     user.sub,
            email:   user.email,
            name:    user.name || user.nickname,
            picture: user.picture,
          },
        }),
      });

      if (!backendResponse.ok) {
        const err = await backendResponse.json().catch(() => ({}));
        throw new Error(err.detail || 'Backend authentication failed');
      }
      backendResponse = await backendResponse.json();
    }

    // Store local JWT and user profile
    if (backendResponse.accessToken) {
      localStorage.setItem('accessToken', backendResponse.accessToken);
      localStorage.setItem('user', JSON.stringify(backendResponse.user));
      console.log('✅ Auth0 login complete, redirecting to dashboard');

      // Redirect to intended destination or dashboard
      const appState = result?.appState;
      const target = appState?.returnTo || '/dashboard.html';
      window.location.href = target;
    } else {
      throw new Error('No access token in backend response');
    }

  } catch (err) {
    console.error('Auth0 callback error:', err);
    window.location.href = `/login.html?error=${encodeURIComponent(err.message)}`;
  }
}

/**
 * Logout from both Auth0 and local session.
 */
async function logoutAuth0() {
  // Clear local storage
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');

  if (auth0Client) {
    try {
      await auth0Client.logout({
        logoutParams: {
          returnTo: AUTH0_CONFIG.logoutUri,
        },
      });
      return; // Auth0 will redirect
    } catch (err) {
      console.warn('Auth0 logout error:', err);
    }
  }

  // Fallback: just redirect
  window.location.href = '/login.html';
}

/**
 * Check if user has an active Auth0 session (for silent re-auth).
 * Returns the user profile if authenticated, null otherwise.
 */
async function checkAuth0Session() {
  if (!auth0Client) await initAuth0();
  if (!auth0Client) return null;

  try {
    const isAuthenticated = await auth0Client.isAuthenticated();
    if (isAuthenticated) {
      return await auth0Client.getUser();
    }
  } catch (err) {
    console.warn('Auth0 session check failed:', err);
  }
  return null;
}

// Auto-initialize on load
document.addEventListener('DOMContentLoaded', () => {
  // Only init if Auth0 SDK is loaded and we have valid config
  if (typeof createAuth0Client !== 'undefined' &&
      AUTH0_CONFIG.domain && !AUTH0_CONFIG.domain.startsWith('YOUR_')) {
    initAuth0();
  }
});
