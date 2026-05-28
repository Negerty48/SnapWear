"use client";

export default function BuscarRopa() {
  return (
    <div className="max-w-3xl mx-auto mt-10 text-center">
      <h1 className="text-4xl font-bold mb-4 text-gray-900">Encuentra tu estilo</h1>
      <p className="text-gray-500 mb-8">Sube la foto de la prenda que estás buscando y rastrearemos nuestro catálogo.</p>
      
      <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 bg-white flex flex-col items-center">
        <span className="text-indigo-600 font-bold text-lg mb-2">📥 Arrastra una foto aquí</span>
        <span className="text-gray-400">o haz clic para explorar tus archivos</span>
      </div>
    </div>
  );
}