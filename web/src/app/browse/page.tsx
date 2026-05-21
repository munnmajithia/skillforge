import { Suspense } from 'react';
import type { Metadata } from 'next';
import { fetchSkills, fetchAllTags } from '@/lib/api';
import BrowseClient from './BrowseClient';

export const metadata: Metadata = {
  title: 'Browse Skills — SkillForge',
  description: 'Browse the SkillForge registry of MCP skill packs for AI coding agents.',
};

function BrowseSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-12 bg-gray-900/80 rounded-xl animate-pulse" />
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-8 w-20 bg-gray-900/80 rounded-lg animate-pulse" />
        ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-56 bg-gray-900/50 rounded-2xl animate-pulse" />
        ))}
      </div>
    </div>
  );
}

export default function BrowsePage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
          Browse Skills
        </h1>
        <p className="text-gray-500 mb-10">
          Discover MCP skill packs for your AI coding agent
        </p>

        <Suspense fallback={<BrowseSkeleton />}>
          <BrowseContent />
        </Suspense>
      </div>
    </div>
  );
}

async function BrowseContent() {
  const [skillsResult, tags] = await Promise.all([
    fetchSkills(),
    fetchAllTags(),
  ]);

  return <BrowseClient initialSkills={skillsResult.skills} allTags={tags} />;
}
