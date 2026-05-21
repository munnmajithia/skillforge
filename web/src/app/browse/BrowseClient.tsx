'use client';

import { useState, useCallback } from 'react';
import type { Skill } from '@/lib/api';
import SkillCard from '@/components/SkillCard';
import SearchBar from '@/components/SearchBar';
import TagBadge from '@/components/TagBadge';

interface BrowseClientProps {
  initialSkills: Skill[];
  allTags: string[];
}

export default function BrowseClient({ initialSkills, allTags }: BrowseClientProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());

  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) {
        next.delete(tag);
      } else {
        next.add(tag);
      }
      return next;
    });
  }, []);

  // Client-side filter based on search + selected tags
  const filteredSkills = initialSkills.filter((skill) => {
    const matchesSearch =
      !searchQuery ||
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesTags =
      selectedTags.size === 0 ||
      Array.from(selectedTags).every((t) => skill.tags.includes(t));

    return matchesSearch && matchesTags;
  });

  return (
    <div className="space-y-8">
      {/* Search */}
      <SearchBar onSearch={setSearchQuery} placeholder="Search skills by name, description, or tag..." />

      {/* Tag Filters */}
      <div className="flex flex-wrap gap-2">
        {allTags.map((tag) => (
          <button
            key={tag}
            onClick={() => toggleTag(tag)}
            className={`inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer ${
              selectedTags.has(tag)
                ? 'bg-[#76B900]/20 border-[#76B900]/40 text-[#76B900]'
                : 'bg-gray-800/50 border-gray-700/50 text-gray-400 hover:bg-gray-800 hover:text-gray-200 hover:border-gray-600'
            }`}
          >
            {tag}
            {selectedTags.has(tag) && (
              <svg className="w-3 h-3 ml-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>
        ))}
        {selectedTags.size > 0 && (
          <button
            onClick={() => setSelectedTags(new Set())}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-colors cursor-pointer"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Results */}
      {filteredSkills.length > 0 ? (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Showing <span className="text-gray-300 font-medium">{filteredSkills.length}</span>{' '}
              skill{filteredSkills.length !== 1 ? 's' : ''}
              {searchQuery && (
                <>
                  {' '}for &ldquo;<span className="text-gray-300">{searchQuery}</span>&rdquo;
                </>
              )}
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSkills.map((skill) => (
              <SkillCard key={skill.name} skill={skill} />
            ))}
          </div>
        </>
      ) : (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-white mb-2">No skills found</h3>
          <p className="text-gray-500">
            Try adjusting your search or filters to find what you&apos;re looking for.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedTags(new Set());
            }}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm transition-colors cursor-pointer"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
}
