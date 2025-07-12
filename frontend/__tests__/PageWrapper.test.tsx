import { render } from '@testing-library/react';
import PageWrapper from '@/components/PageWrapper';
import React from 'react';

// Mock Framer Motion
jest.mock('framer-motion', () => {
    const original = jest.requireActual('framer-motion');
    return {
        ...original,
        motion: {
            ...original.motion,
            div: ({ children, ...props }: { children: React.ReactNode;[key: string]: any }) => {
                // Remove motion-specific props so they don't appear in snapshot
                const { initial, animate, exit, transition, ...rest } = props;
                return <div {...rest}>{children}</div>;
            },
        },
        AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    };
});

describe('PageWrapper', () => {
  it('renders children and matches snapshot', () => {
    const { container } = render(
      <PageWrapper>
        <div>Hello World</div>
      </PageWrapper>
    );

    // Snapshot testing is a good way to verify that the UI doesn't change unexpectedly.
    // The first time this test runs, it will create a snapshot file.
    // Subsequent runs will compare the rendered output to this snapshot.
    expect(container.firstChild).toMatchSnapshot();
  });

  it('applies className when provided', () => {
    const { getByText } = render(
      <PageWrapper className="custom-class">
        <div>Content with custom class</div>
      </PageWrapper>
    );
    const wrapperDiv = getByText('Content with custom class').parentElement;
    expect(wrapperDiv).toHaveClass('custom-class');
  });
});
