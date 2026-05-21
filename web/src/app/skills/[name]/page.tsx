import { Suspense } from 'react';
import type { Metadata } from 'next';
import { fetchSkill } from '@/lib/api';
import SkillDetailClient from './SkillDetailClient';

interface Props {
  params: Promise<{ name: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { name } = await params;
  const result = await fetchSkill(name);
  if (!result) {
    return { title: 'Skill Not Found' };
  }
  return {
    title: `${result.skill.name} — SkillForge`,
    description: result.skill.description.slice(0, 160),
  };
}

function DetailSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-pulse">
      <div className="h-8 w-48 bg-gray-800 rounded-lg" />
      <div className="h-6 w-32 bg-gray-800 rounded-lg" />
      <div className="space-y-2">
        <div className="h-4 bg-gray-800 rounded w-full" />
        <div className="h-4 bg-gray-800 rounded w-3/4" />
      </div>
      <div className="flex gap-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-6 w-20 bg-gray-800 rounded-lg" />
        ))}
      </div>
    </div>
  );
}

export default function SkillDetailPage({ params }: Props) {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20">
        <Suspense fallback={<DetailSkeleton />}>
          <SkillDetailContent params={params} />
        </Suspense>
      </div>
    </div>
  );
}

async function SkillDetailContent({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const result = await fetchSkill(name);

  if (!result) {
    return (
      <div className="text-center py-20">
        <div className="text-5xl mb-4">🔮</div>
        <h2 className="text-2xl font-bold text-white mb-2">Skill Not Found</h2>
        <p className="text-gray-500 mb-6">
          The skill &ldquo;<span className="text-gray-300 font-mono">{name}</span>&rdquo; doesn&apos;t exist in the registry.
        </p>
        <a
          href="/browse"
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#76B900] hover:bg-[#8cd600] text-black font-semibold rounded-xl transition-all"
        >
          ← Back to Browse
        </a>
      </div>
    );
  }

  return <SkillDetailClient skill={result.skill} />;
}
