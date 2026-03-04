/**
 * Composable for managing search state and debounced search execution.
 * Integrates with a provided search API function.
 */

import { ref, watch } from 'vue';
import { debounce } from 'lodash-es'; // Make sure lodash-es is installed

export function useSearch(searchFunction, delay = 500) {
  const query = ref('');
  const results = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // Debounced search function
  const debouncedSearch = debounce(async (searchQuery) => {
    if (!searchQuery.trim()) {
      results.value = [];
      error.value = null;
      loading.value = false;
      return;
    }

    try {
      loading.value = true;
      error.value = null;
      const response = await searchFunction(searchQuery);
      results.value = response.data.list || response.data || []; // Adapt to your API response structure
    } catch (err) {
      console.error('Search error:', err);
      error.value = err;
      results.value = [];
    } finally {
      loading.value = false;
    }
  }, delay);

  // Watch for query changes and trigger search
  watch(query, (newQuery) => {
    debouncedSearch(newQuery);
  });

  const executeSearch = (searchQuery) => {
    // Allows manual triggering without relying on watch
    query.value = searchQuery;
    // The watch will automatically call debouncedSearch
  };

  const clearResults = () => {
    query.value = '';
    results.value = [];
    error.value = null;
  };

  return {
    query,
    results,
    loading,
    error,
    executeSearch, // Can be called manually
    clearResults,
  };
}