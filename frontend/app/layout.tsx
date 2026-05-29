import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SnapWear - Fashion E-commerce',
  description: 'Descubre las mejores prendas de moda en SnapWear',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>
        {children}
      </body>
    </html>
  )
}
