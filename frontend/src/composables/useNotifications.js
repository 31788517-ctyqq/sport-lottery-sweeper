/**
 * Composable for managing application-level notifications.
 * Uses Element Plus/Element UI Message or Notification component.
 * Can be extended to integrate with a backend notification service.
 */

import { ref } from 'vue';
import { ElNotification, ElMessage } from 'element-plus'; // Or element-ui

// Type definition for a notification item
// interface NotificationItem {
//   id: number;
//   title: string;
//   message: string;
//   type: 'success' | 'warning' | 'info' | 'error';
//   duration?: number;
//   timestamp: Date;
// }

const notifications = ref([]);

let nextId = 1;

const showNotification = ({ title, message, type = 'info', duration = 4500 }) => {
  const id = nextId++;
  const notification = {
    id,
    title,
    message,
    type,
    timestamp: new Date(),
  };

  notifications.value.unshift(notification);

  // Use ElNotification for persistent notifications
  ElNotification({
    title,
    message,
    type,
    duration,
    onClose: () => {
      // Optional: Remove from local list when closed manually
      // const index = notifications.value.findIndex(n => n.id === id);
      // if (index > -1) notifications.value.splice(index, 1);
    }
  });
};

const showMessage = ({ message, type = 'info', duration = 3000 }) => {
  // Use ElMessage for simpler, shorter messages
  ElMessage({
    message,
    type,
    duration,
  });
};

const clearNotifications = () => {
  notifications.value = [];
};

// Convenience functions for common types
const showSuccess = (message, title = 'Success') => showNotification({ title, message, type: 'success' });
const showError = (message, title = 'Error') => showNotification({ title, message, type: 'error' });
const showWarning = (message, title = 'Warning') => showNotification({ title, message, type: 'warning' });
const showInfo = (message, title = 'Info') => showNotification({ title, message, type: 'info' });

export function useNotifications() {
  return {
    notifications: readonly(notifications), // Read-only list of notifications
    showNotification,
    showMessage,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearNotifications,
  };
}