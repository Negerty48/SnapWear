import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Trendy Market',
  description: 'Descubre las mejores prendas de moda en Trendy Market',
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
