import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'tests/e2e/support/e2e.js',
    specPattern: 'tests/e2e/specs/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1920,
    viewportHeight: 1080,
    video: false,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // 可以在这里添加节点事件监听器
    }
  },
  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite'
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}'
  }
})