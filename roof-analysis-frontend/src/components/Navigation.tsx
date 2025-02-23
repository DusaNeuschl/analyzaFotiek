// src/components/Navigation.tsx
import { useRouter } from 'next/router';
import Link from 'next/link';

export const Navigation = () => {
  const router = useRouter();

  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex gap-4">
        <Link 
          href="/" 
          className={`px-4 py-2 rounded ${
            router.pathname === '/' ? 'bg-gray-600' : 'hover:bg-gray-700'
          }`}
        >
          Import a Analýza
        </Link>
        <Link 
          href="/visualization" 
          className={`px-4 py-2 rounded ${
            router.pathname === '/visualization' ? 'bg-gray-600' : 'hover:bg-gray-700'
          }`}
        >
          Vizualizácia Dát
        </Link>
      </div>
    </nav>
  );
};