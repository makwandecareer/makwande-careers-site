// config.js - Auto Apply App Frontend Environment Configuration with UI Logic Integration

/**
 * Environment variable configuration for the frontend
 * Used throughout UI to enable/disable features dynamically
 */

// === API & Backend ===
export const backend_url = "https://autoapply-api.onrender.com/api/jobs"; // Backend API base

// === Payment Gateway Keys (used in payment UI integration) ===
export const stripe_public_key = "pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxx";
export const paystack_public_key = "pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxx";

// === App Info ===
export const support_email = "admin@makwandecareer.co.za"; // Updated support email
export const frontend_app_version = "v1_0_0"; // Version displayed in footer
export const default_country = "south_africa"; // Used in job filters and forms
export const default_currency = "zar"; // Used in pricing display

// === UI Behavior Flags ===
export const auth_required = true; // Show/hide login UI components
export const subscription_required = true; // Gate app access behind payment
export const show_demo_jobs = false; // Used to toggle mock/demo jobs if backend is down
export const referral_bonus_active = false; // Future: referral banner or share link

// === Limits and UX Settings ===
export const cv_upload_max_size_mb = 5; // Enforced in upload input (frontend only)
export const api_timeout_seconds = 10; // Used in fetch timeout fallback

// === Contact & Legal Info ===
export const contact_phone = "+27XXXXXXXXX"; // Optional for contact section
export const feedback_url = "https://forms.gle/your_feedback_form"; // Link from footer
export const legal_terms_url = "https://makwandecareers.com/terms"; // Link from signup/login
