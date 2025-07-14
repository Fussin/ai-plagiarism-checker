import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HistoryPage from '@/app/history/page';
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

// Mock components used by HistoryPage
jest.mock('@/components/PageWrapper', () => ({ children }: { children: React.ReactNode }) => <div data-testid="page-wrapper">{children}</div>);

// Mock fetch API
global.fetch = jest.fn();

const mockHistoryData = [
    { id: 1, content_type: 'text_input', timestamp: new Date().toISOString(), originality_score: 0.95, input_snippet: 'This is a test snippet.' },
    { id: 2, content_type: 'file_pdf', file_name: 'report.pdf', timestamp: new Date().toISOString(), originality_score: 0.85, input_snippet: 'PDF content snippet.' },
    { id: 3, content_type: 'image_png', file_name: 'logo.png', timestamp: new Date().toISOString(), originality_score: 0.75, input_snippet: 'Image hash...' },
    { id: 4, content_type: 'video_mp4', file_name: 'demo.mp4', timestamp: new Date().toISOString(), originality_score: 0.65, input_snippet: 'Video transcription...' },
];

describe('HistoryPage', () => {

  beforeEach(() => {
    mockAuthContext.mockClear();
    (global.fetch as jest.Mock).mockClear();
  });

  it('redirects to login if user is not authenticated', () => {
    const mockReplace = jest.fn();
    jest.spyOn(require('next/navigation'), 'useRouter').mockImplementation(() => ({
        replace: mockReplace,
    }));

    mockAuthContext.mockReturnValue({ user: null, isLoading: false });
    render(<HistoryPage />);
    expect(mockReplace).toHaveBeenCalledWith('/login?message=Please login to view history');
  });

  it('fetches and displays history items in card view by default', async () => {
    mockAuthContext.mockReturnValue({ user: { email: 'test@test.com' }, token: 'fake-token', isLoading: false });
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockHistoryData),
    });

    render(<HistoryPage />);

    expect(await screen.findByText('Scan History')).toBeInTheDocument();
    expect(await screen.findByText('text input')).toBeInTheDocument(); // from content_type
    expect(await screen.findByText('report.pdf')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'View Details' })).toHaveLength(4);
  });

  it('switches to table view and displays items', async () => {
    mockAuthContext.mockReturnValue({ user: { email: 'test@test.com' }, token: 'fake-token', isLoading: false });
    (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockHistoryData),
    });

    render(<HistoryPage />);

    // Wait for initial card view to render
    expect(await screen.findByText('report.pdf')).toBeInTheDocument();

    // Find and click the table view button
    const tableViewButton = screen.getByRole('button', { name: /list view/i }); // Assuming aria-label or similar
    await userEvent.click(tableViewButton);

    // Check for table headers
    expect(screen.getByRole('columnheader', { name: 'Content' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Date' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Score (%)' })).toBeInTheDocument();

    // Check for table row content
    expect(screen.getByRole('cell', { name: 'report.pdf' })).toBeInTheDocument();
  });

  it('filters history items based on selection', async () => {
    mockAuthContext.mockReturnValue({ user: { email: 'test@test.com' }, token: 'fake-token', isLoading: false });
    (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockHistoryData),
    });

    render(<HistoryPage />);

    // Wait for initial full list
    expect(await screen.findAllByRole('button', { name: 'View Details' })).toHaveLength(4);

    // Select 'Image' from the filter dropdown
    const filterSelect = screen.getByRole('combobox');
    await userEvent.selectOptions(filterSelect, 'image');

    // Now only one item should be visible
    expect(await screen.findAllByRole('button', { name: 'View Details' })).toHaveLength(1);
    expect(screen.getByText('logo.png')).toBeInTheDocument();
    expect(screen.queryByText('report.pdf')).not.toBeInTheDocument();
  });

});
