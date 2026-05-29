'use client';

import Image from 'next/image';
import { Anuncio } from '@/lib/api';

interface AnuncioCardProps {
  anuncio: Anuncio;
  onClick: () => void;
}

export default function AnuncioCard({ anuncio, onClick }: AnuncioCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer transform hover:scale-105 transition-transform"
    >
      {/* Image Container */}
      <div className="relative w-full h-64 bg-gray-200">
        {anuncio.imagen_url ? (
          <Image
            src={anuncio.imagen_url}
            alt={`Anuncio ${anuncio.id}`}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-300">
            <span className="text-gray-500">Sin imagen</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Precio */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl font-bold text-blue-600">
            ${anuncio.precio.toFixed(2)}
          </span>
        </div>

        {/* Descripción truncada */}
        {anuncio.descripcion && (
          <p className="text-gray-700 text-sm line-clamp-2 mb-3">
            {anuncio.descripcion}
          </p>
        )}

        {/* Seller Info */}
        {anuncio.vendedor_id && (
          <p className="text-xs text-gray-500">
            Vendedor: {anuncio.vendedor_id}
          </p>
        )}

        {/* Ver Detalles Button */}
        <button className="w-full mt-3 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium">
          Ver Detalles
        </button>
      </div>
    </div>
  );
}
