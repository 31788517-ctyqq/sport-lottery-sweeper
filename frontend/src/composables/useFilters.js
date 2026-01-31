/**
 * Composable for managing filter state across the application.
 * Uses provide/inject pattern or a shared store concept if combined with Pinia/Vuex.
 * Here, we create a reactive state object that can be managed centrally.
 */

// AI_WORKING: coder1 @2026-01-29 - 添加 watch 导入，修复未定义错误
import { ref, reactive, computed, watch } from 'vue';
import { filtersAPI } from '@/api/modules/filters';

// Centralized filter state object
const filterState = reactive({
  selectedSport: '',
  selectedLeague: '',
  dateRange: [], // [start, end] dates
  searchQuery: '',
  intelligenceCategory: '',
  intelligencePriority: '',
  // Add more filter fields as needed
});

// Options fetched from API
const options = reactive({
  sports: [],
  leagues: [],
  categories: [],
  priorities: [],
  loading: false,
});

const loadOptions = async () => {
  options.loading = true;
  try {
    // Fetch all necessary options in parallel
    const [sportsRes, categoriesRes, prioritiesRes] = await Promise.allSettled([
      filtersAPI.getSports(),
      filtersAPI.getIntelligenceCategories(),
      filtersAPI.getIntelligencePriorities(),
    ]);

    if (sportsRes.status === 'fulfilled') {
      options.sports = sportsRes.value.data || [];
    } else {
      console.error('Failed to load sports:', sportsRes.reason);
    }
    if (categoriesRes.status === 'fulfilled') {
      options.categories = categoriesRes.value.data || [];
    } else {
      console.error('Failed to load categories:', categoriesRes.reason);
    }
    if (prioritiesRes.status === 'fulfilled') {
      options.priorities = prioritiesRes.value.data || [];
    } else {
      console.error('Failed to load priorities:', prioritiesRes.reason);
    }
  } catch (error) {
    console.error('Error loading filter options:', error);
  } finally {
    options.loading = false;
  }
};

// Computed properties for derived state
const activeFiltersCount = computed(() => {
  let count = 0;
  if (filterState.selectedSport) count++;
  if (filterState.selectedLeague) count++;
  if (filterState.dateRange.length > 0) count++;
  if (filterState.searchQuery) count++;
  if (filterState.intelligenceCategory) count++;
  if (filterState.intelligencePriority) count++;
  // Add other checks as needed
  return count;
});

const resetFilters = () => {
  Object.keys(filterState).forEach(key => {
    if (Array.isArray(filterState[key])) {
      filterState[key] = [];
    } else {
      filterState[key] = '';
    }
  });
};

// Watch for selectedSport change to load corresponding leagues
watch(() => filterState.selectedSport, async (newSport) => {
  if (newSport) {
    try {
      const res = await filtersAPI.getLeaguesBySport(newSport);
      options.leagues = res.data || [];
    } catch (error) {
      console.error('Failed to load leagues for sport:', newSport, error);
      options.leagues = [];
    }
  } else {
    options.leagues = []; // Reset leagues if sport is cleared
  }
});

export function useFilters() {
  return {
    filterState: readonly(filterState), // Make state readonly for consumers
    options: readonly(options),
    activeFiltersCount,
    loadOptions,
    resetFilters,
  };
}