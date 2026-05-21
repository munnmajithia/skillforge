'use client';

import Link from 'next/link';
import { useState } from 'react';
import type { Skill } from '@/lib/api';
import SecurityBadge from '@/components/SecurityBadge';
import TagBadge from '@/components/TagBadge';

interface SkillDetailClientProps {
  skill: Skill;
}

const riskStyles: Record<string, { bg: string; text: string; border: string; label: string }> = {
  low: {
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    border: 'border-emerald-500/20',
    label: 'Low',
  },
  medium: {
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    border: 'border-amber-500/20',
    label: 'Medium',
  },
  high: {
    bg: 'bg-orange-500/10',
    text: 'text-orange-400',
    border: 'border-orange-500/20',
    label: 'High',
  },
  critical: {
    bg: 'bg-red-500/10',
    text: 'text-red-400',
    border: 'border-red-500/20',
    label: 'Critical',
  },
};

export default function SkillDetailClient({ skill }: SkillDetailClientProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(skill.install_command || `skillforge install ${skill.name}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back link */}
      <Link
        href="/browse"
        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-300 transition-colors mb-8"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 12H5m0 0l7 7m-7-7l7-7" />
        </svg>
        Back to Browse
      </Link>

      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <h1 className="text-3xl sm:text-4xl font-bold text-white font-mono">
            {skill.name}
          </h1>
          <span className="px-3 py-1 bg-gray-800 rounded-lg text-sm font-mono text-gray-400 border border-gray-800">
            v{skill.version}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm">
          <span className="text-gray-400">
            by <span className="text-white font-medium">{skill.author}</span>
          </span>
          {skill.license && (
            <span className="text-gray-600">{skill.license}</span>
          )}
          <div className="flex items-center gap-1 text-gray-600">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            {skill.downloads.toLocaleString()} installs
          </div>
          {skill.updated_at && (
            <span className="text-gray-600">
              Updated {new Date(skill.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          )}
        </div>
      </div>

      {/* Scores */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div className="p-5 rounded-2xl bg-gray-900/50 border border-gray-800/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Security Score</span>
            <SecurityBadge score={skill.security_score} />
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                skill.security_score >= 80
                  ? 'bg-emerald-500'
                  : skill.security_score >= 50
                  ? 'bg-amber-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${skill.security_score}%` }}
            />
          </div>
        </div>
        <div className="p-5 rounded-2xl bg-gray-900/50 border border-gray-800/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Validation Score</span>
            <span className="text-sm font-medium text-blue-400">{skill.validation_score}/100</span>
          </div>
          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full"
              style={{ width: `${skill.validation_score}%` }}
            />
          </div>
        </div>
      </div>

      {/* Description */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-3">Description</h2>
        <p className="text-gray-400 leading-relaxed">{skill.description}</p>
      </div>

      {/* Tags */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-3">Tags</h2>
        <div className="flex flex-wrap gap-2">
          {skill.tags.map((tag) => (
            <TagBadge key={tag} tag={tag} clickable />
          ))}
        </div>
      </div>

      {/* Permissions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-3">
          Permissions{' '}
          <span className="text-sm font-normal text-gray-500">
            ({skill.permissions.length} tool{skill.permissions.length !== 1 ? 's' : ''})
          </span>
        </h2>
        <div className="space-y-2">
          {skill.permissions.map((perm) => {
            const style = riskStyles[perm.risk] || riskStyles.low;
            return (
              <div
                key={perm.tool}
                className={`flex items-start gap-3 p-3 rounded-xl border ${style.border} ${style.bg}`}
              >
                <span
                  className={`mt-0.5 px-2 py-0.5 rounded-md text-xs font-medium border ${style.border} ${style.bg} ${style.text}`}
                >
                  {style.label}
                </span>
                <div>
                  <code className="text-sm text-gray-200 font-mono">{perm.tool}</code>
                  {perm.description && (
                    <p className="text-xs text-gray-500 mt-0.5">{perm.description}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Install */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-3">Install</h2>
        <div className="relative bg-gray-900/80 rounded-2xl border border-gray-800 p-5 font-mono">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-[#76B900]">$</span>
            <span className="text-gray-300">skillforge</span>
            <span className="text-gray-400">install</span>
            <span className="text-[#76B900]">{skill.name}</span>
          </div>
          <button
            onClick={handleCopy}
            className="absolute top-4 right-4 flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs font-medium transition-colors cursor-pointer"
          >
            {copied ? (
              <>
                <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span className="text-gray-400">Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Links */}
      <div className="flex flex-wrap gap-4">
        {skill.repository && (
          <a
            href={skill.repository}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-800/50 hover:bg-gray-800 text-gray-300 rounded-xl border border-gray-700/50 hover:border-gray-600 text-sm font-medium transition-all"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            View Repository
          </a>
        )}
        {skill.homepage && (
          <a
            href={skill.homepage}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-800/50 hover:bg-gray-800 text-gray-300 rounded-xl border border-gray-700/50 hover:border-gray-600 text-sm font-medium transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Homepage
          </a>
        )}
      </div>

      {/* Category badge */}
      {skill.category && (
        <div className="mt-8 pt-6 border-t border-gray-800/50">
          <span className="inline-flex items-center px-3 py-1 rounded-lg text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {skill.category}
          </span>
        </div>
      )}
    </div>
  );
}
