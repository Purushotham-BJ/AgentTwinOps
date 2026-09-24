import React from 'react';

interface Column<T> {
  key: string;
  header: string;
  width?: string;
  render: (row: T) => React.ReactNode;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  onRowClick?: (row: T) => void;
}

export function Table<T>({ columns, data, keyExtractor, onRowClick }: TableProps<T>) {
  return (
    <div style={{ overflowX: 'auto', width: '100%' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', tableLayout: 'fixed' }}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                style={{
                  textAlign: 'left',
                  padding: 'var(--space-3) var(--space-4)',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 'var(--font-semibold)',
                  color: 'var(--color-text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  borderBottom: '1px solid var(--color-border)',
                  width: col.width,
                  whiteSpace: 'nowrap',
                }}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={keyExtractor(row)}
              onClick={() => onRowClick?.(row)}
              style={{
                borderBottom: '1px solid var(--color-border-subtle)',
                transition: 'background var(--transition-fast)',
                cursor: onRowClick ? 'pointer' : undefined,
              }}
              onMouseEnter={(e) => { if (onRowClick) e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  style={{
                    padding: 'var(--space-3) var(--space-4)',
                    fontSize: 'var(--text-sm)',
                    color: 'var(--color-text-secondary)',
                    verticalAlign: 'middle',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
