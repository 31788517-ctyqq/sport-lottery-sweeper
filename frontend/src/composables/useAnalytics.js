/**
 * Composable for integrating analytics tracking (e.g., Google Analytics, Mixpanel).
 * Provides generic methods to track page views, events, and user properties.
 * Requires the analytics SDK to be initialized separately (e.g., in main.js).
 */

import { getCurrentInstance } from 'vue';

export function useAnalytics() {
  const instance = getCurrentInstance();

  const trackPageView = (path) => {
    // Example using gtag (Google Analytics)
    if (window.gtag) {
      window.gtag('config', 'GA_MEASUREMENT_ID', { page_path: path }); // Replace GA_MEASUREMENT_ID
    }
    // Example using a generic tracker
    // if (window.analytics) {
    //   window.analytics.page(path);
    // }
    console.log('[Analytics] Page View Tracked:', path); // Dev log
  };

  const trackEvent = (eventName, properties = {}) => {
    // Example using gtag
    if (window.gtag) {
      window.gtag('event', eventName, properties);
    }
    // Example using a generic tracker
    // if (window.analytics) {
    //   window.analytics.track(eventName, properties);
    // }
    console.log('[Analytics] Event Tracked:', eventName, properties); // Dev log
  };

  // Example: Track specific component view
  const trackComponentView = (componentName) => {
    trackEvent('component_view', { component: componentName });
  };

  // Lifecycle hook integration (optional, requires instance)
  if (instance) {
    // Example: Track when component is mounted
    onMounted(() => {
        trackComponentView(instance.type.name || 'AnonymousComponent');
    });
  }


  return {
    trackPageView,
    trackEvent,
    trackComponentView,
  };
}