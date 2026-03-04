/**
 * Composable for managing pagination state and logic.
 * Handles current page, page size, total items, and calculates page count.
 */

import { ref, computed } from 'vue';

export function usePagination(defaultPageSize = 10) {
  const currentPage = ref(1);
  const pageSize = ref(defaultPageSize);
  const totalItems = ref(0);

  const pageCount = computed(() => Math.ceil(totalItems.value / pageSize.value));

  const setPagination = (page, size, total) => {
    currentPage.value = page;
    pageSize.value = size;
    totalItems.value = total;
  };

  const resetPage = () => {
    currentPage.value = 1;
  };

  const goToPage = (page) => {
    if (page >= 1 && page <= pageCount.value) {
      currentPage.value = page;
    }
  };

  const nextPage = () => {
    if (currentPage.value < pageCount.value) {
      currentPage.value++;
    }
  };

  const prevPage = () => {
    if (currentPage.value > 1) {
      currentPage.value--;
    }
  };

  return {
    currentPage: readonly(currentPage),
    pageSize: readonly(pageSize),
    totalItems: readonly(totalItems),
    pageCount,
    setPagination,
    resetPage,
    goToPage,
    nextPage,
    prevPage,
  };
}