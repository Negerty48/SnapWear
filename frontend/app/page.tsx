'use client';

import { useEffect, useState } from 'react';
import AnuncioCard from '@/components/AnuncioCard';
import AnuncioModal from '@/components/AnuncioModal';
import SubirAnuncioModal from '@/components/SubirAnuncioModal';
import BuscarPorFotoModal from '@/components/BuscarPorFotoModal';
import { fetchAnuncios, Anuncio, AnunciosResponse } from '@/lib/api';

export default function Home() {
  const [anuncios, setAnuncios] = useState<Anuncio[]>([]);
  const [selectedAnuncio, setSelectedAnuncio] = useState<Anuncio | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubirModalOpen, setIsSubirModalOpen] = useState(false);
  const [isBuscarModalOpen, setIsBuscarModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  const ITEMS_PER_PAGE = 40;
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE);

  const loadAnuncios = async (page: number) => {
    try {
      setIsLoading(true);
      setError(null);
      const skip = (page - 1) * ITEMS_PER_PAGE;
      const response = await fetchAnuncios(skip, ITEMS_PER_PAGE);
      setAnuncios(response.items);
      setTotal(response.total);
    } catch (err) {
      setError('Error al cargar los anuncios');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch announcements when page changes
  useEffect(() => {
    loadAnuncios(currentPage);
  }, [currentPage]);

  const handleSelectAnuncio = (anuncio: Anuncio) => {
    setSelectedAnuncio(anuncio);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedAnuncio(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Trendy Market</h1>
            <p className="text-gray-600 mt-1">Descubre las mejores prendas de moda</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setIsBuscarModalOpen(true)}
              className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 px-6 rounded-lg transition-colors shadow-sm flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Buscar por Foto
            </button>
            <button
              onClick={() => setIsSubirModalOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors shadow-sm flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Subir Anuncio
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Info Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {total > 0 ? `${total} Anuncios Disponibles` : 'Cargando anuncios...'}
          </h2>
          <p className="text-gray-600">
            Explora nuestra colección de prendas de moda únicas y de alta calidad
          </p>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800 font-medium">{error}</p>
            <p className="text-red-600 text-sm mt-1">
              Asegúrate de que el backend está ejecutándose en http://localhost:8000
            </p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin">
              <svg className="h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <p className="text-gray-600 mt-4">Cargando anuncios...</p>
          </div>
        )}

        {/* Announcements Grid */}
        {!isLoading && anuncios.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {anuncios.map((anuncio) => (
              <AnuncioCard
                key={anuncio.id}
                anuncio={anuncio}
                onClick={() => handleSelectAnuncio(anuncio)}
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && anuncios.length === 0 && !error && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">
              No hay anuncios disponibles
            </h3>
            <p className="mt-1 text-gray-600">
              Intenta más tarde o verifica que el backend está corriendo
            </p>
          </div>
        )}

        {/* Pagination */}
        {!isLoading && totalPages > 1 && (
          <div className="flex justify-center items-center space-x-4 mt-12">
            <button
              onClick={() => {
                setCurrentPage(p => Math.max(1, p - 1));
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              disabled={currentPage === 1}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-gray-700 bg-white"
            >
              {"<"}
            </button>

            <div className="flex items-center space-x-2">
              {/* Always show page 1 */}
              <span
                className={`px-4 py-2 rounded-lg font-medium shadow-sm cursor-pointer transition-colors ${currentPage === 1 ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 text-gray-700'}`}
                onClick={() => { setCurrentPage(1); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
              >
                1
              </span>

              {/* Left ellipsis */}
              {currentPage > 2 && <span className="px-2 text-gray-400 font-medium">...</span>}

              {/* Current Page (if not 1 and not last) */}
              {currentPage !== 1 && currentPage !== totalPages && (
                <span className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium shadow-sm">
                  {currentPage}
                </span>
              )}

              {/* Right ellipsis */}
              {currentPage < totalPages - 1 && <span className="px-2 text-gray-400 font-medium">...</span>}

              {/* Always show last page if totalPages > 1 */}
              {totalPages > 1 && (
                <span
                  className={`px-4 py-2 rounded-lg font-medium shadow-sm cursor-pointer transition-colors ${currentPage === totalPages ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 text-gray-700'}`}
                  onClick={() => { setCurrentPage(totalPages); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                >
                  {totalPages}
                </span>
              )}
            </div>

            <button
              onClick={() => {
                setCurrentPage(p => Math.min(totalPages, p + 1));
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-gray-700 bg-white"
            >
              {">"}
            </button>
          </div>
        )}
      </main>

      {/* Modal de Detalles */}
      <AnuncioModal
        anuncio={selectedAnuncio}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSelectSimilar={handleSelectAnuncio}
      />

      {/* Modal de Subida */}
      <SubirAnuncioModal
        isOpen={isSubirModalOpen}
        onClose={() => setIsSubirModalOpen(false)}
        onSuccess={() => loadAnuncios(1)} // Al subir, recargar la primera página
      />

      {/* Modal de Búsqueda por Foto */}
      <BuscarPorFotoModal
        isOpen={isBuscarModalOpen}
        onClose={() => setIsBuscarModalOpen(false)}
        onSelectResult={handleSelectAnuncio}
      />

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-bold mb-4">Trendy Market</h3>
              <p className="text-gray-400">
                La mejor plataforma para comprar y vender prendas de moda
              </p>
            </div>
            <div>
              <h3 className="text-lg font-bold mb-4">Enlaces</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Inicio
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Sobre nosotros
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Contacto
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-bold mb-4">Legal</h3>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Términos de Servicio
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Privacidad
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2026 Trendy Market. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
