import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI 內容趨勢雷達',
  description: 'AI 內容趨勢雷達 MVP Scaffold',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant">
      <body>{children}</body>
    </html>
  );
}
