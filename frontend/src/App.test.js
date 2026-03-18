import { render, screen } from '@testing-library/react';
import App from './App';

test('renders simple reconciliation ui', () => {
  render(<App />);
  expect(screen.getByText(/clinical reconciliation engine/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /run ai reconciliation/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /run data quality check/i })).toBeInTheDocument();
});
