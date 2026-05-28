"use client";
import { useState } from 'react';

export default function SubirAnuncio() {
  const [foto, setFoto] = useState(null);
  const [fotoPreview, setFotoPreview] = useState(null);
  const [precio, setPrecio] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [cargando, setCargando] = useState(false);

  const manejarFoto = (e) => {
    const archivo = e.target.files[0];
    setFoto(archivo);
    setFotoPreview(URL.createObjectURL(archivo));
  };

  const publicarAnuncio = async (e) => {
    e.preventDefault();
    setCargando(true);

    const formData = new FormData();
    formData.append("foto", foto);
    formData.append("precio", precio);
    formData.append("descripcion", descripcion);

    try {
      // AQUÍ VA LA URL DE TU API EN AZURE
      const respuesta = await fetch("https://TU_API_EN_AZURE.azurewebsites.net/subir_prenda", {
        method: "POST",
        body: formData,
      });

      if (respuesta.ok) {
        alert("¡Prenda publicada con éxito!");
      } else {
        alert("Error al publicar.");
      }
    } catch (error) {
      alert("Error de conexión con el servidor.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto bg-white p-8 rounded-xl shadow-sm border mt-10">
      <h1 className="text-3xl font-bold mb-2">Vende tu ropa</h1>
      
      <form className="flex flex-col gap-6" onSubmit={publicarAnuncio}>
        <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-center bg-gray-50 hover:bg-gray-100 transition-colors h-64 overflow-hidden">
          
          {/* El input "fantasma" ahora solo vive dentro de este div gracias al 'absolute' */}
          <input 
            type="file" 
            accept="image/*" 
            onChange={manejarFoto}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          />

          {/* Contenido visual */}
          {fotoPreview ? (
            <img src={fotoPreview} alt="Prenda" className="h-full object-contain" />
          ) : (
            <div className="z-0">
              <span className="text-indigo-600 font-semibold">Haz clic para subir una foto</span>
              <p className="text-sm mt-1 text-gray-500">PNG, JPG hasta 5MB</p>
            </div>
          )}
        </div>

        <input 
            type="text" 
            placeholder="Descripción"
            onChange={(e) => setDescripcion(e.target.value)}
            className="w-full border rounded-lg p-3"
            required
        />
        
        <input 
            type="number" 
            placeholder="Precio (€)"
            onChange={(e) => setPrecio(e.target.value)}
            className="w-full border rounded-lg p-3"
            required
        />

        <button 
            type="submit" 
            disabled={cargando}
            className="w-full bg-indigo-600 text-white font-bold py-3 rounded-lg hover:bg-indigo-700 transition-colors"
        >
          {cargando ? "Publicando..." : "Publicar Anuncio"}
        </button>
      </form>
    </div>
  );
}