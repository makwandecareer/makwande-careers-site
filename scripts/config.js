/**
 * Global configuration for the AutoApply frontend.
 * This file should be included BEFORE any other scripts
 * so that window.__CONFIG__ is available everywhere.
 */

window.__CONFIG__ = {
    // Absolute URL of your deployed FastAPI backend
    // Replace this with your actual Render backend URL
    API_BASE_URL: "https://autoapply-api.onrender.com",

    // Optional: version or environment label for debugging
    APP_VERSION: "1.0.0",
    ENVIRONMENT: "production"
};

/**
 * Example usage in other JS files:
 * fetch(`${window.__CONFIG__.API_BASE_URL}/auth/login`, { ... })
 */

