import Link from 'next/link';
import type { Skill } from '@/lib/api';
import SecurityBadge from './SecurityBadge';
import TagBadge from './TagBadge';

interface SkillCardProps {
  skill: Skill;
}

export default function SkillCard({ skill }: SkillCardProps) {
  return (
    <Link
      href={`/skills/${skill.name}`}
      className="group block p-6 rounded-2xl bg-gradient-to-b from-gray-800/50 to-gray-900/50 border border-gray-800/50 hover:border-[#76B900]/30 hover:from-gray-800/80 hover:to-gray-900/80 transition-all duration-300 hover:shadow-lg hover:shadow-[#76B900]/5"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-white group-hover:text-[#76B900] transition-colors">
          {skill.name}
        </h3>
        <span className="text-xs font-mono text-gray-500 bg-gray-800/50 px-2 py-1 rounded-md border border-gray-800">
          v{skill.version}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-400 leading-relaxed mb-4 line-clamp-2">
        {skill.description}
      </p>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        {skill.tags.slice(0, 4).map((tag) => (
          <TagBadge key={tag} tag={tag} />
        ))}
        {skill.tags.length > 4 && (
          <span className="text-xs text-gray-600 px-2 py-0.5">
            +{skill.tags.length - 4}
          </span>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-800/50">
        <div className="flex items-center gap-3">
          <SecurityBadge score={skill.security_score} />
          <span className="text-xs text-gray-500">
            by <span className="text-gray-400">{skill.author}</span>
          </span>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-600">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          {skill.downloads.toLocaleString()}
        </div>
      </div>
    </Link>
  );
}
