import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import Navbar from '@/components/Navbar';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: {
    default: 'SkillForge — MCP Skill Registry',
    template: '%s | SkillForge',
  },
  description:
    'Discover, install, and publish MCP Skill Packs for AI coding agents. The open registry for Claude Code, Cursor, Codex, and more.',
  keywords: ['MCP', 'skills', 'AI', 'coding agents', 'Claude Code', 'Cursor', 'registry'],
  authors: [{ name: 'Munn Majithia' }],
  openGraph: {
    title: 'SkillForge — MCP Skill Registry',
    description: 'Discover, install, and publish MCP Skill Packs for AI coding agents.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#0a0a0a] text-gray-100">
        <Navbar />
        <main className="flex-1 pt-16">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

function Footer() {
  return (
    <footer className="border-t border-gray-800/50 bg-[#0a0a0a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              Built by{' '}
              <a
                href="https://github.com/munnmajithia"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-[#76B900] transition-colors"
              >
                Munn Majithia
              </a>
            </span>
            <span className="text-gray-700">·</span>
            <span className="text-sm text-gray-600">SkillForge © {new Date().getFullYear()}</span>
          </div>
          <div className="flex items-center gap-6">
            <a
              href="/browse"
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              Browse
            </a>
            <a
              href="/about"
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              About
            </a>
            <a
              href="https://github.com/munnmajithia/skillforge"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-gray-300 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
