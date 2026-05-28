import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center px-4">
      <h1 className="text-5xl font-extrabold text-gray-900 mb-6 tracking-tight">
        Tu ropa favorita, <span className="text-indigo-600">a un escaneo de distancia.</span>
      </h1>
      <p className="text-xl text-gray-500 mb-10 max-w-2xl">
        Únete al mercado de segunda mano inteligente. Sube una foto de lo que buscas y nuestra IA encontrará prendas idénticas para ti.
      </p>
      <div className="flex gap-4">
        <Link href="/buscar" className="bg-indigo-600 text-white font-bold py-3 px-8 rounded-full hover:bg-indigo-700 transition shadow-lg">
          Buscar por Foto
        </Link>
        <Link href="/subir" className="bg-white text-indigo-600 font-bold py-3 px-8 rounded-full border-2 border-indigo-600 hover:bg-indigo-50 transition shadow-sm">
          Vender Ropa
        </Link>
      </div>
    </div>
  );
}