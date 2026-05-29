'use client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Anuncio {
  id: number;
  precio: number;
  imagen_url: string;
  descripcion?: string;
  vendedor_id?: string;
  vector_clip?: number[];
}

export interface AnunciosResponse {
  total: number;
  items: Anuncio[];
}

/**
 * Fetch all announcements from the backend API
 */
export async function fetchAnuncios(
  skip: number = 0,
  limit: number = 100,
  vendedor_id?: string
): Promise<AnunciosResponse> {
  try {
    let url = `${API_BASE_URL}/anuncios?skip=${skip}&limit=${limit}`;
    
    if (vendedor_id) {
      url += `&vendedor_id=${vendedor_id}`;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data as AnunciosResponse;
  } catch (error) {
    console.error('Error fetching announcements:', error);
    throw error;
  }
}

/**
 * Fetch a single announcement by ID
 */
export async function fetchAnuncio(id: number): Promise<Anuncio> {
  try {
    const url = `${API_BASE_URL}/anuncios/${id}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data as Anuncio;
  } catch (error) {
    console.error('Error fetching announcement:', error);
    throw error;
  }
}

/**
 * Fetch similar announcements by ID
 */
export async function fetchAnunciosSimilares(id: number): Promise<AnunciosResponse> {
  try {
    const url = `${API_BASE_URL}/anuncios/${id}/similares`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data as AnunciosResponse;
  } catch (error) {
    console.error('Error fetching similar announcements:', error);
    throw error;
  }
}

/**
 * Create a new announcement (with image upload)
 */
export async function crearAnuncio(formData: FormData): Promise<Anuncio> {
  try {
    const url = `${API_BASE_URL}/anuncios`;

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data as Anuncio;
  } catch (error) {
    console.error('Error creating announcement:', error);
    throw error;
  }
}

/**
 * Visual search by image
 */
export async function buscarAnunciosPorImagen(formData: FormData): Promise<AnunciosResponse> {
  try {
    const url = `${API_BASE_URL}/anuncios/buscar`;

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data as AnunciosResponse;
  } catch (error) {
    console.error('Error in visual search:', error);
    throw error;
  }
}

export interface Deteccion {
  index: number;
  base64_image: string;
}

/**
 * Detect clothing items in an image (file or URL)
 */
export async function detectarPrendas(formData: FormData): Promise<Deteccion[]> {
  try {
    const url = `${API_BASE_URL}/ai/detect`;
    
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return data.detections as Deteccion[];
  } catch (error) {
    console.error('Error detecting clothing:', error);
    throw error;
  }
}



