import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import prettier from 'eslint-config-prettier'
import tsParser from '@typescript-eslint/parser'
import vueParser from 'vue-eslint-parser'

const isProd = process.env.NODE_ENV === 'production'

const disableRules = (rules) =>
  Object.fromEntries(Object.keys(rules || {}).map((key) => [key, 'off']))

const disabledBaseRules = {
  ...disableRules(js.configs.recommended.rules),
  ...disableRules(vue.configs['flat/recommended'].rules)
}

export default [
  {
    ignores: ['dist', 'node_modules', 'coverage', 'cypress', 'src/tests/**', 'src/utils/mockDataManager.js']
  },
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  prettier,
  {
    rules: {
      ...disabledBaseRules,
      // 自定义规则
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off',
      'vue/no-deprecated-slot-attribute': 'off',
      'vue/no-deprecated-slot-scope-attribute': 'off',
      'vue/no-deprecated-v-on-native-modifier': 'off',
      'vue/no-deprecated-filter': 'off',
      'vue/no-unused-components': 'off',
      'vue/no-mutating-props': 'off',
      'vue/require-explicit-emits': 'off',
      'vue/no-template-shadow': 'off',
      'vue/v-slot-style': 'off',
      'vue/first-attribute-linebreak': 'off',
      'vue/order-in-components': 'off',
      'vue/html-self-closing': 'off',
      'vue/attributes-order': 'off',
      'vue/attribute-hyphenation': 'off',
      'no-dupe-keys': 'off',
      'no-console': isProd ? 'warn' : 'off',
      'no-debugger': isProd ? 'warn' : 'off',
      'no-undef': 'off',
      'no-constant-condition': 'off',
      'no-unused-vars': 'off',
      'vue/no-unused-vars': 'off',
      'vue/require-default-prop': 'off',
      'vue/html-closing-bracket-newline': 'off',
    }
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
        extraFileExtensions: ['.vue']
      }
    }
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    }
  }
]
