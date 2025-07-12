import { render, screen } from '@testing-library/react';
import HeaderNav from '@/components/HeaderNav';
import { AuthContextType } from '@/contexts/AuthContext';
import React from 'react';

// Mock the AuthContext
const mockAuthContext = jest.fn();
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext(),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock ThemeToggleButton as it's not relevant to this test
jest.mock('@/components/ThemeToggleButton', () => {
    return function DummyThemeToggleButton() {
        return <div data-testid="theme-toggle-button"></div>;
    }
});


describe('HeaderNav', () => {

  it('renders login and register links when user is not authenticated', () => {
    // Setup mock return value for unauthenticated state
    mockAuthContext.mockReturnValue({
      user: null,
      isLoading: false,
      logout: jest.fn(),
    });

    render(<HeaderNav />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Register')).toBeInTheDocument();
    expect(screen.queryByText('History')).not.toBeInTheDocument();
    expect(screen.queryByText('Logout')).not.toBeInTheDocument();
  });

  it('renders history, user email, and logout button when user is authenticated', () => {
    // Setup mock return value for authenticated state
    const mockUser = { email: 'test@example.com', id: 1, is_active: true };
    mockAuthContext.mockReturnValue({
      user: mockUser,
      isLoading: false,
      logout: jest.fn(),
    });

    render(<HeaderNav />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText(/Welcome, test@example.com/i)).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();
    expect(screen.queryByText('Register')).not.toBeInTheDocument();
  });

  it('renders a loading state when auth is loading', () => {
     // Setup mock return value for loading state
     mockAuthContext.mockReturnValue({
        user: null,
        isLoading: true,
        logout: jest.fn(),
      });

      render(<HeaderNav />);

      // The loading state is a div with pulse animation, we can check for its presence
      // or if other links are hidden.
      expect(screen.queryByText('Login')).not.toBeInTheDocument();
      expect(screen.queryByText('Logout')).not.toBeInTheDocument();
      // A better test might involve a data-testid on the loading placeholder
      // For now, checking for the absence of other links is a reasonable check.
  });

});
