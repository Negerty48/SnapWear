-- SQL Schema for SnapWear Backend
-- This matches the existing PostgreSQL database structure

-- Create anuncios table (if not exists)
CREATE TABLE IF NOT EXISTS anuncios (
    id INTEGER PRIMARY KEY,
    precio DOUBLE PRECISION NOT NULL,
    vector_clip vector(512),
    vendedor_id CHARACTER VARYING,
    imagen_url CHARACTER VARYING NOT NULL,
    descripcion CHARACTER VARYING
);

-- Create index on vendedor_id for faster queries
CREATE INDEX IF NOT EXISTS idx_anuncios_vendedor_id ON anuncios(vendedor_id);

-- Enable pgvector extension (run this once in your database)
-- CREATE EXTENSION IF NOT EXISTS vector;
