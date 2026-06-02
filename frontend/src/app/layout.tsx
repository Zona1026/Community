import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI 趨勢探索平台',
  description: 'AI 趨勢探索平台 MVP Scaffold',
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
