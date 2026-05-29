# SnapWear Frontend

Frontend de Next.js (App Router) para la plataforma de e-commerce SnapWear.

## Estructura

```
frontend/
├── app/
│   ├── layout.tsx          # Layout raíz
│   ├── page.tsx            # Página principal (grid de anuncios)
│   ├── globals.css         # Estilos globales
│   └── page.module.css     # Estilos específicos
├── components/
│   ├── AnuncioCard.tsx     # Tarjeta del anuncio (grid)
│   └── AnuncioModal.tsx    # Modal de detalles
├── lib/
│   ├── api.ts              # Cliente de API (backend)
│   └── azure-storage.ts    # Integración con Azure Blob Storage
├── public/                 # Assets estáticos
├── .env.local              # Variables de entorno (no comitear)
├── .env.example            # Plantilla de variables
├── package.json
├── tsconfig.json
├── next.config.js
├── postcss.config.js
└── tailwind.config.ts
```

## Setup

### 1. Instalar dependencias

```bash
npm install
```

### 2. Configurar variables de entorno

Copiar `.env.example` a `.env.local`:

```bash
cp .env.example .env.local
```

Las variables necesarias son:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AZURE_STORAGE_CONNECTION_STRING=your_connection_string
NEXT_PUBLIC_BLOB_CONTAINER_NAME=photos
```

### 3. Ejecutar en desarrollo

```bash
npm run dev
```

El frontend estará disponible en http://localhost:3000

### 4. Build para producción

```bash
npm run build
npm start
```

## Características

✅ **Grid Responsivo**: 4 columnas en desktop, 2 en tablet, 1 en mobile
✅ **Tarjetas de Anuncios**: Muestra precio e imagen desde Azure Blob Storage
✅ **Modal de Detalles**: Ver información completa del anuncio
✅ **Integración con Backend**: Consume API FastAPI en `http://localhost:8000`
✅ **Tailwind CSS**: Diseño moderno y responsive
✅ **Manejo de Errores**: Mensajes claros si el backend no está disponible
✅ **Loading States**: Spinners y estados mientras se cargan datos
✅ **Azure Blob Storage**: Imágenes desde `trendysa.blob.core.windows.net`

## Páginas

### Página Principal (`/`)
- Grid de anuncios (4 por fila)
- Tarjetas con:
  - Imagen
  - Precio
  - Descripción truncada
  - Botón "Ver Detalles"
- Modal al hacer click en una tarjeta

## Componentes

### `AnuncioCard` (`components/AnuncioCard.tsx`)
Tarjeta individual del anuncio en el grid:
- Imagen del producto
- Precio en grande
- Descripción truncada
- ID del vendedor
- Botón interactivo

**Props:**
```typescript
{
  anuncio: Anuncio
  onClick: () => void
}
```

### `AnuncioModal` (`components/AnuncioModal.tsx`)
Modal con detalles completos del anuncio:
- Imagen en grande
- Precio destacado
- Descripción completa
- ID del anuncio
- Información del vendedor
- Información del vector CLIP

**Props:**
```typescript
{
  anuncio: Anuncio | null
  isOpen: boolean
  onClose: () => void
}
```

## APIs

### `lib/api.ts`

#### `fetchAnuncios(skip?, limit?, vendedor_id?)`
```typescript
const response = await fetchAnuncios(0, 100, 'seller123');
// Returns: { total: number, items: Anuncio[] }
```

#### `fetchAnuncio(id)`
```typescript
const anuncio = await fetchAnuncio(1);
// Returns: Anuncio
```

## Integración con Backend

El frontend se conecta al backend FastAPI en:

```
GET http://localhost:8000/anuncios
GET http://localhost:8000/anuncios/{id}
```

**Asegúrate de que:**
1. El backend está corriendo: `uvicorn app.main:app --reload`
2. CORS está configurado para `http://localhost:3000`
3. La base de datos tiene datos

## Azure Blob Storage

Las imágenes se obtienen desde:

```
https://trendysa.blob.core.windows.net/photos/{imagen_url}
```

La conexión string está en `.env.local` y se usa para:
- Validar acceso a los blobs
- Generar URLs firmadas (si es necesario)

## Tailwind CSS

- Configurado en `tailwind.config.ts`
- Estilos globales en `app/globals.css`
- Grid responsivo: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- Clases de utilidad para diseño

## Deployment

### Vercel (Recomendado para Next.js)

```bash
npm install -g vercel
vercel
```

### Variables de entorno en Vercel

Añadir en Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://backend-url.com
NEXT_PUBLIC_AZURE_STORAGE_CONNECTION_STRING=...
NEXT_PUBLIC_BLOB_CONTAINER_NAME=photos
```

## Scripts npm

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Ejecutar en desarrollo |
| `npm run build` | Compilar para producción |
| `npm start` | Ejecutar versión compilada |
| `npm run lint` | Ejecutar ESLint |

## Troubleshooting

### "Cannot reach backend"
- Verificar que el backend está ejecutándose en `http://localhost:8000`
- Verificar CORS en `backend/app/main.py`
- Verificar que `NEXT_PUBLIC_API_URL` es correcto

### Imágenes no cargan
- Verificar que `NEXT_PUBLIC_AZURE_STORAGE_CONNECTION_STRING` es correcto
- Verificar que la URL de la imagen existe en Azure Storage
- Verificar permisos de la cuenta de storage

### "JSX not allowed"
- Asegurar que los componentes tienen `'use client'` al inicio si usan hooks

## Dependencias

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "next": "^14.0.0",
  "@azure/storage-blob": "^12.16.0"
}
```
