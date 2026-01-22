/**
 * 模拟用户数据API
 */
export const mockUsersAPI = {
  getCurrentUser() {
    console.warn('[Mock API] Fetching current user info');
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          success: true,
          data: { id: 1, username: 'mock_user', role: 'user' },
          message: 'Success'
        });
      }, 200);
    });
  },
  // ... 其他mock方法
};