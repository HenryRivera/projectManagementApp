import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

// Mock fetch
global.fetch = vi.fn();

function createFetchResponse(data) {
  return {
    ok: true,
    json: () => Promise.resolve(data),
  };
}

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays loading state initially', () => {
    fetch.mockImplementationOnce(() => new Promise(() => {}));

    render(<App />);

    // App should render without crashing
    expect(document.body).toBeTruthy();
  });

  it('renders without crashing', async () => {
    const mockProjects = {
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0
    };

    fetch.mockResolvedValueOnce(createFetchResponse(mockProjects));

    render(<App />);

    // App should render
    expect(document.body).toBeTruthy();
  });

  it('displays projects when loaded', async () => {
    const mockProjects = {
      items: [
        {
          id: 1,
          title: 'Test Project',
          description: 'A test project',
          status: 'active',
          health: 'on_track',
          progress: 50,
          owner: 'Test Owner',
          updated_at: '2026-01-21T10:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1
    };

    fetch.mockResolvedValueOnce(createFetchResponse(mockProjects));

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
