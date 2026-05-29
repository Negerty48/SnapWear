'use client';

import { useState, useRef } from 'react';
import { buscarAnunciosPorImagen, Anuncio } from '@/lib/api';
import Image from 'next/image';
import AnuncioCard from './AnuncioCard';

interface BuscarPorFotoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectResult: (anuncio: Anuncio) => void;
}

export default function BuscarPorFotoModal({ isOpen, onClose, onSelectResult }: BuscarPorFotoModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<Anuncio[] | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const resetState = () => {
    setFile(null);
    setPreview(null);
    setResults(null);
    setError(null);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      const url = URL.createObjectURL(selected);
      setPreview(url);
      setResults(null); // Clear previous results when a new image is chosen
    }
  };

  const handleSearch = async () => {
    if (!file) {
      setError("Por favor, selecciona una imagen.");
      return;
    }
    
    try {
      setIsSubmitting(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await buscarAnunciosPorImagen(formData);
      setResults(response.items);
      
    } catch (err: any) {
      setError(err.message || 'Error al buscar anuncios');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="sticky top-0 bg-white p-6 border-b flex justify-between items-center z-10">
          <h2 className="text-2xl font-bold">Buscar por Foto</h2>
          <button onClick={handleClose} className="text-gray-500 hover:text-gray-700 text-2xl font-bold">✕</button>
        </div>
        
        <div className="p-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">Selecciona la imagen de la prenda</label>
              <div 
                className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${preview ? 'border-blue-300 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'}`}
                onClick={() => fileInputRef.current?.click()}
              >
                {preview ? (
                  <div className="relative w-full h-64">
                    <Image src={preview} alt="Preview" fill className="object-contain" />
                  </div>
                ) : (
                  <div className="py-16 text-gray-500 flex flex-col items-center">
                    <svg className="w-12 h-12 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Haz clic para subir una foto
                  </div>
                )}
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="image/*" 
                onChange={handleFileChange}
              />

              <button 
                onClick={handleSearch}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
                disabled={!file || isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="h-5 w-5 rounded-full border-2 border-white border-t-transparent animate-spin"></div>
                    Analizando con IA...
                  </>
                ) : (
                  'Buscar Prendas Similares'
                )}
              </button>
            </div>

            {/* Results Section */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">Resultados</label>
              
              {!results && !isSubmitting && (
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-gray-500">Sube una foto y busca para ver resultados</p>
                </div>
              )}

              {isSubmitting && (
                <div className="h-64 flex flex-col items-center justify-center bg-gray-50 rounded-lg border border-gray-200">
                  <div className="h-8 w-8 rounded-full border-4 border-blue-600 border-t-transparent animate-spin mb-4"></div>
                  <p className="text-gray-600">Procesando y buscando similitudes...</p>
                </div>
              )}

              {results && (
                <div className="space-y-4">
                  {results.length > 0 ? (
                    <div className="grid grid-cols-2 gap-4">
                      {results.map(anuncio => (
                        <div key={anuncio.id} onClick={() => { onSelectResult(anuncio); handleClose(); }} className="cursor-pointer hover:ring-2 hover:ring-blue-500 rounded-lg transition-all">
                          <AnuncioCard anuncio={anuncio} onClick={() => {}} />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-8">No se encontraron prendas similares.</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
