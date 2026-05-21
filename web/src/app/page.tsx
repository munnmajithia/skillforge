import type { Metadata } from 'next';
import Link from 'next/link';
import CopyButton from '@/components/CopyButton';

export const metadata: Metadata = {
  title: 'SkillForge — MCP Skill Packs for AI Coding Agents',
  description:
    'Discover, install, and publish MCP Skill Packs. The open registry for Claude Code, Cursor, Codex, and more.',
};

const features = [
  {
    emoji: '🔌',
    title: 'MCP-Native',
    description: 'Skills are built on the Model Context Protocol — drop-in support for any MCP-compatible agent.',
  },
  {
    emoji: '🔒',
    title: 'Security Scanned',
    description: 'Every skill is analyzed for risky tool permissions with a transparent security score.',
  },
  {
    emoji: '📦',
    title: 'Version Controlled',
    description: 'Semantic versioning for every skill pack. Always know what you\'re installing.',
  },
  {
    emoji: '🤖',
    title: 'Agent-Ready',
    description: 'Built for Claude Code, Cursor, Codex, Windsurf, and any tool that speaks MCP.',
  },
];

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-[#76B900]/10 rounded-full blur-3xl glow-pulse" />
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-[#76B900]/5 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20 sm:pt-32 sm:pb-28">
          <div className="text-center max-w-3xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#76B900]/10 border border-[#76B900]/20 text-[#76B900] text-sm font-medium mb-8 animate-fade-in-up">
              <span className="w-2 h-2 rounded-full bg-[#76B900]" />
              MCP Skill Registry
            </div>

            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white mb-6 animate-fade-in-up [animation-delay:100ms] [animation-fill-mode:backwards]">
              Skill
              <span className="text-[#76B900]">Forge</span>
            </h1>

            <p className="text-lg sm:text-xl text-gray-400 mb-4 animate-fade-in-up [animation-delay:200ms] [animation-fill-mode:backwards]">
              MCP Skill Packs for AI Coding Agents
            </p>

            <p className="text-base text-gray-500 max-w-xl mx-auto mb-10 animate-fade-in-up [animation-delay:300ms] [animation-fill-mode:backwards]">
              Discover, install, and publish skills for Claude Code, Cursor, Codex, and more.
              Extend your AI agent with community-built capabilities.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up [animation-delay:400ms] [animation-fill-mode:backwards]">
              <Link
                href="/browse"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-[#76B900] hover:bg-[#8cd600] text-black font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-[#76B900]/25 active:scale-[0.98]"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Browse Skills
              </Link>
              <a
                href="https://github.com/munnmajithia/skillforge"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-gray-800/50 hover:bg-gray-800 text-gray-300 font-semibold rounded-xl border border-gray-700/50 hover:border-gray-600 transition-all"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                </svg>
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Install */}
      <section className="border-t border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
              Get Started in Seconds
            </h2>
            <p className="text-gray-500 max-w-lg mx-auto">
              One command to install. No configuration needed. Works with any MCP-compatible agent.
            </p>
          </div>
          <div className="max-w-xl mx-auto">
            <div className="relative bg-gray-900/80 rounded-2xl border border-gray-800 p-6 font-mono text-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[#76B900]">$</span>
                <span className="text-gray-300">skillforge</span>
                <span className="text-gray-400">install</span>
                <span className="text-[#76B900]">github-code-review</span>
              </div>
              <CopyButton text="skillforge install github-code-review" />
            </div>
            <p className="text-center text-xs text-gray-600 mt-4">
              Works with Claude Code, Cursor, Codex, Windsurf, and other MCP agents
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
              Why SkillForge?
            </h2>
            <p className="text-gray-500 max-w-lg mx-auto">
              The registry built from the ground up for AI agent skills.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group p-6 rounded-2xl bg-gray-900/40 border border-gray-800/50 hover:border-[#76B900]/20 hover:bg-gray-900/60 transition-all duration-300"
              >
                <div className="text-3xl mb-4">{feature.emoji}</div>
                <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-[#76B900] transition-colors">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats / CTA */}
      <section className="border-t border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <div className="text-center bg-gradient-to-b from-gray-900/80 to-gray-900/40 rounded-3xl border border-gray-800/50 p-10 sm:p-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
              Ready to Extend Your Agent?
            </h2>
            <p className="text-gray-400 max-w-md mx-auto mb-8">
              Browse the registry, find skills that match your workflow, and install them with a single command.
            </p>
            <Link
              href="/browse"
              className="inline-flex items-center gap-2 px-8 py-3.5 bg-[#76B900] hover:bg-[#8cd600] text-black font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-[#76B900]/25 active:scale-[0.98]"
            >
              Explore Skills
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
