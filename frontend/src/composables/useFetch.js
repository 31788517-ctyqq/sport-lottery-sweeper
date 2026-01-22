/**
 * Generic Vue 3 Composable for Data Fetching with Loading and Error States
 * Provides a reusable way to handle API calls within components.
 */

import { ref, shallowRef } from 'vue';

export function useFetch(fetchFunction, immediate = true, initialData = null) {
  const data = shallowRef(initialData);
  const error = ref(null);
  const loading = ref(false);

  const execute = async (...args) => {
    loading.value = true;
    error.value = null;
    data.value = initialData; // Reset data on new request if needed

    try {
      const result = await fetchFunction(...args);
      data.value = result;
    } catch (err) {
      console.error('Fetch error:', err);
      error.value = err;
    } finally {
      loading.value = false;
    }
  };

  if (immediate) {
    // Execute immediately when composable is used
    // Note: This relies on the fetchFunction being ready when this runs
    // It's often better to call execute() manually from the component after setup
    // setTimeout(execute, 0); // Run after setup
  }

  return {
    data,
    error,
    loading,
    execute, // Call this to trigger the fetch
  };
}