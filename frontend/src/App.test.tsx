import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

describe('App', () => {
  it('renders the home screen', () => {
    render(<App />);
    expect(screen.getByText(/Choose your language/i)).toBeInTheDocument();
  });

  it('keeps the brand button available as a home shortcut', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole('button', { name: /Start lobby/i }));
    expect(screen.getByRole('button', { name: /Multi Wordle/i })).toBeInTheDocument();
  });
});
