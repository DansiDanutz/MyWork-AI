// Server component - force dynamic to prevent SSG prerendering
export const dynamic = 'force-dynamic';
export const runtime = 'edge';

export default function NotFound() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#f9fafb'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{
          fontSize: '6rem',
          fontWeight: 'bold',
          color: '#6366f1',
          marginBottom: '1rem'
        }}>
          404
        </h1>
        <h2 style={{
          fontSize: '1.5rem',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '0.5rem'
        }}>
          Page not found
        </h2>
        <p style={{
          fontSize: '1rem',
          color: '#6b7280',
          marginBottom: '2rem'
        }}>
          The page you are looking for does not exist.
        </p>
        <a
          href="/"
          style={{
            display: 'inline-block',
            padding: '0.75rem 1.5rem',
            backgroundColor: '#6366f1',
            color: 'white',
            borderRadius: '0.5rem',
            textDecoration: 'none',
            fontWeight: '500'
          }}
        >
          Go Home
        </a>
      </div>
    </div>
  );
}
