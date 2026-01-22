/**
 * Composable for managing a single WebSocket connection.
 * Provides methods to connect, disconnect, send messages, and listen for events.
 */

import { ref, onUnmounted } from 'vue';

export function useWebSocket(url, protocols = null) {
  const socket = ref(null);
  const isConnected = ref(false);
  const error = ref(null);

  const connect = () => {
    if (socket.value) {
      console.warn('WebSocket is already connected.');
      return;
    }

    try {
      socket.value = new WebSocket(url, protocols);

      socket.value.onopen = (event) => {
        console.log('WebSocket Connected:', event);
        isConnected.value = true;
        error.value = null;
      };

      socket.value.onmessage = (event) => {
        // console.log('WebSocket Message Received:', event.data);
        // Emit or handle the received message
        // Example: mitt.emit('ws-message', JSON.parse(event.data));
        emit('message', JSON.parse(event.data));
      };

      socket.value.onerror = (event) => {
        console.error('WebSocket Error:', event);
        error.value = event;
      };

      socket.value.onclose = (event) => {
        console.log('WebSocket Disconnected:', event.code, event.reason);
        isConnected.value = false;
        socket.value = null;
        // Optionally attempt reconnection here based on event.code
      };
    } catch (e) {
      console.error('Failed to create WebSocket:', e);
      error.value = e;
    }
  };

  const disconnect = () => {
    if (socket.value) {
      socket.value.close();
      socket.value = null;
      isConnected.value = false;
    }
  };

  const send = (data) => {
    if (isConnected.value && socket.value) {
      socket.value.send(JSON.stringify(data));
    } else {
      console.error('Cannot send message, WebSocket is not connected.');
    }
  };

  // Attempt to close connection when composable is unmounted
  onUnmounted(() => {
    disconnect();
  });

  return {
    socket: readonly(socket),
    isConnected: readonly(isConnected),
    error: readonly(error),
    connect,
    disconnect,
    send,
  };
}