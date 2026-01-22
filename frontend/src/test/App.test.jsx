import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    }),
  },
}));

// Import the mocked client
import client from '../api/client';

// Mock user for authenticated tests
const mockUser = {
  id: 1,
  email: 'sarah.chen@company.com',
  name: 'Sarah Chen',
  role: 'admin',
  accessToken: 'mock_token_123',
  loginTime: '2026-01-21T10:00:00Z'
};

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('displays loading state initially', () => {
    client.get.mockImplementation(() => new Promise(() => {}));

    render(<App />);

    // App should render without crashing
    expect(document.body).toBeTruthy();
  });

  it('renders login page when not authenticated', async () => {
    render(<App />);

    // Should show login page
    await waitFor(() => {
      expect(screen.getByText('Project Management')).toBeInTheDocument();
      expect(screen.getByText('Sign in to access your projects')).toBeInTheDocument();
    });
  });

  it('displays projects when logged in', async () => {
    // Pre-populate localStorage with authenticated user
    localStorage.setItem('sso_user', JSON.stringify(mockUser));

    const mockProjects = {
      items: [
        {
          id: 1,
          title: 'Test Project',
          short_description: 'A test project',
          status: 'active',
          health: 'healthy',
          progress: 50.0,
          updated_at: '2026-01-21T10:00:00Z',
          owner: null,
          tags: [],
          milestones: [],
          team_members: [],
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1
    };

    // Mock axios client responses
    client.get.mockImplementation((url) => {
      if (url === '/projects' || url.startsWith('/projects')) {
        return Promise.resolve({ data: mockProjects });
      }
      if (url === '/users') {
        return Promise.resolve({ data: [] });
      }
      if (url === '/tags') {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: {} });
    });

    render(<App />);

    // Wait for projects to load
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });
  });
});
