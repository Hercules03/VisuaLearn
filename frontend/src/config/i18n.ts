/**
 * i18next Configuration
 * Multi-language support for the frontend (English, Japanese)
 * Uses namespace organization and browser language detection
 */

import i18next from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';

/**
 * Supported languages
 */
export const SUPPORTED_LANGUAGES = {
  en: { name: 'English', nativeName: 'English', flag: '🇺🇸' },
  ja: { name: 'Japanese', nativeName: '日本語', flag: '🇯🇵' },
} as const;

export type Language = keyof typeof SUPPORTED_LANGUAGES;

/**
 * Initialize i18next
 */
export async function initializeI18n(): Promise<typeof i18next> {
  await i18next
    // Load translation files via HTTP
    .use(HttpBackend)
    // Detect user language from browser/localStorage
    .use(LanguageDetector)
    // Initialize i18next
    .init(
      {
        // Fallback language
        fallbackLng: 'en',

        // Support multiple languages
        supportedLngs: Object.keys(SUPPORTED_LANGUAGES),

        // Namespaces for organizing translations
        ns: ['common'],
        defaultNS: 'common',

        // Default language if detection fails
        lng: 'en',

        // Interpolation options
        interpolation: {
          // Disable escaping HTML in interpolated values
          escapeValue: false,
        },

        // Load translations after page loads
        load: 'languageOnly',

        // Use implicit keys (allow using nested keys with dot notation)
        keySeparator: '.',
        nsSeparator: ':',
      },
      (err: any) => {
        if (err) console.error('i18next initialization error:', err);
      }
    );

  // Configure backend options separately
  i18next.options.backend = {
    loadPath: '/locales/{{lng}}/{{ns}}.json',
    addPath: '/locales/add/{{lng}}/{{ns}}',
  };

  // Configure language detection
  i18next.options.detection = {
    order: ['localStorage', 'navigator', 'htmlTag'],
    caches: ['localStorage'],
  };

  return i18next;
}

/**
 * Get current language
 */
export function getCurrentLanguage(): Language {
  const lng = i18next.language;
  return (Object.keys(SUPPORTED_LANGUAGES).includes(lng) ? lng : 'en') as Language;
}

/**
 * Change language
 */
export async function changeLanguage(lng: Language): Promise<void> {
  await i18next.changeLanguage(lng);
  // Store preference in localStorage
  localStorage.setItem('i18nextLng', lng);
  // Update HTML lang attribute
  document.documentElement.lang = lng;
}

/**
 * Get language info
 */
export function getLanguageInfo(lng: Language): typeof SUPPORTED_LANGUAGES[Language] {
  return SUPPORTED_LANGUAGES[lng];
}

/**
 * Translate key with optional namespace
 */
export function t(key: string, options?: Record<string, any>): string {
  return i18next.t(key, options);
}

export default i18next;
