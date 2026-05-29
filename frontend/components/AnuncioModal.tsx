'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { Anuncio, buscarAnunciosPorImagen, detectarPrendas, Deteccion } from '@/lib/api';

interface AnuncioModalProps {
  anuncio: Anuncio | null;
  isOpen: boolean;
  onClose: () => void;
  onSelectSimilar?: (anuncio: Anuncio) => void;
}

export default function AnuncioModal({ anuncio, isOpen, onClose, onSelectSimilar }: AnuncioModalProps) {
  const [similares, setSimilares] = useState<Anuncio[]>([]);
  const [isLoadingSimilares, setIsLoadingSimilares] = useState(false);
  
  const [detections, setDetections] = useState<Deteccion[] | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [selectedBoxIndex, setSelectedBoxIndex] = useState<number | null>(null);

  // When modal opens, fetch detections
  useEffect(() => {
    if (isOpen && anuncio?.imagen_url) {
      const loadDetections = async () => {
        setIsDetecting(true);
        setDetections(null);
        setSelectedBoxIndex(null);
        setSimilares([]);
        
        try {
          const formData = new FormData();
          formData.append('url', anuncio.imagen_url);
          // Only passing URL, file is empty
          const data = await detectarPrendas(formData);
          setDetections(data);
          if (data.length > 0) {
            setSelectedBoxIndex(data[0].index); // Automatically select the first one
          }
        } catch (error) {
          console.error("Error al detectar prendas", error);
        } finally {
          setIsDetecting(false);
        }
      };
      loadDetections();
    } else {
      setDetections(null);
      setSelectedBoxIndex(null);
      setSimilares([]);
    }
  }, [isOpen, anuncio?.imagen_url]);

  // When selectedBoxIndex changes, fetch similares for that specific crop
  useEffect(() => {
    if (isOpen && anuncio?.imagen_url && selectedBoxIndex !== null) {
      const loadSimilares = async () => {
        setIsLoadingSimilares(true);
        try {
          const formData = new FormData();
          formData.append('url', anuncio.imagen_url);
          formData.append('box_index', selectedBoxIndex.toString());
          const response = await buscarAnunciosPorImagen(formData);
          
          // Filter out the current announcement from results
          const filteredItems = response.items.filter(item => item.id !== anuncio.id);
          setSimilares(filteredItems.slice(0, 3)); // Ensure max 3 are shown
        } catch (error) {
          console.error("Error al cargar similares", error);
        } finally {
          setIsLoadingSimilares(false);
        }
      };
      loadSimilares();
    }
  }, [isOpen, anuncio?.imagen_url, anuncio?.id, selectedBoxIndex]);

  if (!isOpen || !anuncio) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header con botón cerrar */}
        <div className="sticky top-0 flex justify-between items-center p-6 border-b bg-white z-10">
          <h2 className="text-2xl font-bold">Detalles del Anuncio</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ✕
          </button>
        </div>

        {/* Contenido */}
        <div className="p-6">
          {/* Imagen */}
          <div className="relative w-full h-96 bg-gray-100 rounded-lg mb-6 overflow-hidden">
            {anuncio.imagen_url ? (
              <Image
                src={anuncio.imagen_url}
                alt={`Anuncio ${anuncio.id}`}
                fill
                className="object-contain"
                sizes="(max-width: 768px) 100vw, 600px"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gray-300">
                <span className="text-gray-500 text-lg">Sin imagen disponible</span>
              </div>
            )}
          </div>

          {/* Precio grande */}
          <div className="mb-6">
            <p className="text-gray-500 text-sm mb-2">Precio</p>
            <h3 className="text-4xl font-bold text-blue-600 mb-4">
              ${anuncio.precio.toFixed(2)}
            </h3>
          </div>

          {/* Descripción */}
          {anuncio.descripcion && (
            <div className="mb-6">
              <p className="text-gray-500 text-sm mb-2">Descripción</p>
              <p className="text-gray-800 whitespace-pre-wrap">
                {anuncio.descripcion}
              </p>
            </div>
          )}

          {/* Vendedor */}
          {anuncio.vendedor_id && (
            <div className="mb-6">
              <p className="text-gray-500 text-sm mb-2">Vendedor</p>
              <p className="text-gray-800 font-medium">{anuncio.vendedor_id}</p>
            </div>
          )}

          {/* Acciones */}
          <div className="flex gap-3 pt-6 border-t mb-8">
            <button className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium">
              Contactar Vendedor
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-800 py-3 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Cerrar
            </button>
          </div>

          {/* Selector de Prendas Detectadas */}
          {(isDetecting || (detections && detections.length > 1)) && (
            <div className="pt-6 border-t mb-8 bg-gray-50 p-4 rounded-xl">
              {isDetecting ? (
                <div className="flex items-center gap-2 text-blue-600">
                  <div className="h-5 w-5 rounded-full border-2 border-blue-600 border-t-transparent animate-spin"></div>
                  <span className="text-sm font-medium">Detectando prendas en la imagen con IA...</span>
                </div>
              ) : detections && detections.length > 1 ? (
                <>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">¿Qué prenda buscas?</h3>
                  <p className="text-sm text-gray-500 mb-4">Selecciona una prenda de la foto para ver otras similares en nuestro catálogo.</p>
                  <div className="flex gap-4 overflow-x-auto py-2">
                    {detections.map((det) => (
                      <div 
                        key={det.index}
                        onClick={() => setSelectedBoxIndex(det.index)}
                        className={`relative shrink-0 w-20 h-20 rounded-lg cursor-pointer overflow-hidden border-4 transition-all ${selectedBoxIndex === det.index ? 'border-blue-600 shadow-md transform scale-105' : 'border-transparent hover:border-gray-300'}`}
                      >
                        <Image src={`data:image/jpeg;base64,${det.base64_image}`} alt={`Deteccion ${det.index}`} fill className="object-cover" />
                      </div>
                    ))}
                  </div>
                </>
              ) : null}
            </div>
          )}

          {/* Anuncios Similares */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-4">Anuncios Similares</h3>
            {isLoadingSimilares ? (
              <div className="flex justify-center py-8">
                <div className="inline-block animate-spin">
                  <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
              </div>
            ) : similares.length > 0 ? (
              <div className="grid grid-cols-3 gap-4">
                {similares.map((sim) => (
                  <div 
                    key={sim.id} 
                    className="cursor-pointer group"
                    onClick={() => onSelectSimilar && onSelectSimilar(sim)}
                  >
                    <div className="relative w-full h-32 bg-gray-200 rounded-lg mb-2 overflow-hidden">
                      {sim.imagen_url ? (
                        <Image
                          src={sim.imagen_url}
                          alt={`Anuncio similar ${sim.id}`}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform"
                          sizes="(max-width: 768px) 33vw, 200px"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gray-300">
                          <span className="text-gray-500 text-xs text-center">Sin imagen</span>
                        </div>
                      )}
                    </div>
                    <p className="font-bold text-blue-600">${sim.precio.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm bg-gray-50 p-4 rounded-lg border border-gray-100 text-center">No se encontraron prendas similares en el catálogo para esta selección.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
