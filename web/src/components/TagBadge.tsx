import Link from 'next/link';

interface TagBadgeProps {
  tag: string;
  clickable?: boolean;
}

export default function TagBadge({ tag, clickable = false }: TagBadgeProps) {
  const baseClasses =
    'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700/50 transition-colors';

  if (clickable) {
    return (
      <Link
        href={`/browse?tag=${tag}`}
        className={`${baseClasses} hover:bg-gray-700 hover:text-gray-200 hover:border-gray-600 cursor-pointer`}
      >
        {tag}
      </Link>
    );
  }

  return <span className={baseClasses}>{tag}</span>;
}
