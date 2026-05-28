import './globals.css'
import Link from 'next/link'

export const metadata = {
  title: 'Trendy Market',
  description: 'Compra y vende ropa de segunda mano con IA',
}

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        
        {/* BARRA DE NAVEGACIÓN SUPERIOR */}
        <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
          <div className="max-w-5xl mx-auto p-4 flex justify-between items-center">
            
            {/* Logo */}
            <Link href="/" className="text-2xl font-extrabold text-indigo-600 tracking-tight">
              TrendyMarket
            </Link>
            
            {/* Botones */}
            <div className="flex gap-4 items-center font-medium">
              <Link href="/" className="hover:text-indigo-600 transition-colors">
                Explorar
              </Link>
              <Link href="/buscar" className="hover:text-indigo-600 transition-colors">
                Búsqueda Visual
              </Link>
              <Link href="/subir" className="bg-indigo-600 text-white px-5 py-2 rounded-full hover:bg-indigo-700 transition-colors shadow-sm">
                Vender
              </Link>
            </div>
            
          </div>
        </nav>

        {/* CONTENIDO DE CADA PÁGINA */}
        <main className="max-w-5xl mx-auto p-4">
          {children}
        </main>
        
      </body>
    </html>
  )
}