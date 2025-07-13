import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from '@/app/login/page';
import { AuthContextType } from '@/contexts/AuthContext';

// Mock the AuthContext
const mockAuthContext = jest.fn();
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext(),
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
}));

// Mock components used by LoginPage
jest.mock('@/components/Spinner', () => () => <div data-testid="spinner"></div>);
jest.mock('@/components/PageWrapper', () => ({ children }: { children: React.ReactNode }) => <>{children}</>);


describe('LoginPage', () => {

  beforeEach(() => {
    // Reset mocks before each test
    mockAuthContext.mockClear();
  });

  it('renders the login form correctly', () => {
    // Setup unauthenticated state
    mockAuthContext.mockReturnValue({
      user: null,
      isLoading: false,
      login: jest.fn().mockResolvedValue({ success: true }),
    });

    render(<LoginPage />);

    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/not a member\?/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty fields on submit', async () => {
    mockAuthContext.mockReturnValue({
        user: null,
        isLoading: false,
        login: jest.fn(),
    });

    render(<LoginPage />);

    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await userEvent.click(submitButton);

    // Expect validation messages for empty fields
    expect(await screen.findByText('Email is required.')).toBeInTheDocument();
    expect(await screen.findByText('Password is required.')).toBeInTheDocument();

    // Ensure login function was not called
    expect(mockAuthContext().login).not.toHaveBeenCalled();
  });

  it('shows validation error for invalid email format', async () => {
    mockAuthContext.mockReturnValue({
        user: null,
        isLoading: false,
        login: jest.fn(),
    });

    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    await userEvent.type(emailInput, 'invalid-email');
    fireEvent.blur(emailInput); // Trigger onBlur validation

    expect(await screen.findByText('Please enter a valid email address.')).toBeInTheDocument();
  });


  it('calls the login function with correct credentials on valid submission', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ success: true });
    mockAuthContext.mockReturnValue({
        user: null,
        isLoading: false,
        login: mockLogin,
    });

    render(<LoginPage />);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledTimes(1);
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  it('displays a form error if login fails', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ success: false, error: 'Invalid credentials from API' });
    mockAuthContext.mockReturnValue({
        user: null,
        isLoading: false,
        login: mockLogin,
    });

    render(<LoginPage />);

    await userEvent.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText('Invalid credentials from API')).toBeInTheDocument();
  });

});
