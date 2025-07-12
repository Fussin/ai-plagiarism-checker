/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    // Handle module aliases
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/contexts/(.*)$': '<rootDir>/contexts/$1',
    '^@/app/(.*)$': '<rootDir>/app/$1',

    // Mock CSS imports
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  // Since we are not using next/jest, we need to handle transpiling node_modules if they use ESM
  // This is a common requirement. For now, let's see if it works without it first.
  // transformIgnorePatterns: ['/node_modules/'],
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json',
    },
  },
};
