import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About — SkillForge',
  description:
    'Learn about SkillForge, the open MCP skill registry for AI coding agents like Claude Code, Cursor, and Codex.',
};

const steps = [
  {
    number: '1',
    title: 'Browse',
    description:
      'Search the registry for skills that match your needs — code review, project management, database tools, and more.',
    emoji: '🔍',
  },
  {
    number: '2',
    title: 'Install',
    description:
      'One command installs the skill into your agent\'s MCP configuration. No setup scripts, no config files.',
    emoji: '📥',
  },
  {
    number: '3',
    title: 'Use',
    description:
      'Your AI agent immediately gains new capabilities. Talk to it naturally — it knows how to use the skill.',
    emoji: '⚡',
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-gray-800/50">
        <div className="absolute inset-0">
          <div className="absolute -top-40 right-0 w-96 h-96 bg-[#76B900]/5 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 sm:pt-28 sm:pb-20">
          <div className="max-w-3xl">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
              What is{' '}
              <span className="text-[#76B900]">SkillForge</span>?
            </h1>
            <p className="text-lg text-gray-400 leading-relaxed">
              SkillForge is an open registry of MCP (Model Context Protocol) Skill Packs — 
              pre-built, security-scanned capabilities that extend what AI coding agents can do. 
              Think of it like an app store for your AI.
            </p>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-b border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-12 text-center">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step) => (
              <div key={step.number} className="relative text-center">
                {/* Connector line for desktop */}
                {step.number !== '3' && (
                  <div className="hidden md:block absolute top-8 left-[calc(50%+3rem)] w-[calc(100%-6rem)] h-px bg-gradient-to-r from-gray-800 to-transparent" />
                )}
                <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-[#76B900]/20 to-[#76B900]/5 border border-[#76B900]/20 flex items-center justify-center text-2xl">
                  {step.emoji}
                </div>
                <div className="text-sm font-mono text-[#76B900] mb-2">Step {step.number}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="border-b border-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-12 text-center">
            Built With
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { name: 'MCP', desc: 'Model Context Protocol for agent-skill communication' },
              { name: 'FastAPI', desc: 'High-performance Python API backend' },
              { name: 'Next.js', desc: 'React framework for the web dashboard' },
              { name: 'LangChain', desc: 'LLM orchestration and tool integration' },
            ].map((tech) => (
              <div
                key={tech.name}
                className="p-6 rounded-2xl bg-gray-900/40 border border-gray-800/50 hover:border-gray-700/50 transition-colors"
              >
                <h3 className="text-lg font-semibold text-white mb-2">{tech.name}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{tech.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Open Source */}
      <section>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
          <div className="text-center max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#76B900]/10 border border-[#76B900]/20 text-[#76B900] text-sm font-medium mb-6">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              Open Source
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
              Open Source & Community Driven
            </h2>
            <p className="text-gray-400 mb-8">
              SkillForge is fully open source. The registry, the CLI, and all skill packs live on GitHub.
              Contributing is easy — fork the repo, create a skill, and open a PR.
            </p>
            <a
              href="https://github.com/munnmajithia/skillforge"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-3.5 bg-gray-800/50 hover:bg-gray-800 text-gray-300 font-semibold rounded-xl border border-gray-700/50 hover:border-gray-600 transition-all"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
              View Source on GitHub
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
