interface SecurityBadgeProps {
  score: number;
  showLabel?: boolean;
}

export default function SecurityBadge({ score, showLabel = true }: SecurityBadgeProps) {
  const color = score >= 80 ? 'green' : score >= 50 ? 'yellow' : 'red';

  const gradients = {
    green: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-400',
    yellow: 'from-amber-500/20 to-amber-600/10 border-amber-500/30 text-amber-400',
    red: 'from-red-500/20 to-red-600/10 border-red-500/30 text-red-400',
  };

  const dots = {
    green: 'bg-emerald-400',
    yellow: 'bg-amber-400',
    red: 'bg-red-400',
  };

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border bg-gradient-to-r ${gradients[color]}`}
      title={`Security Score: ${score}/100`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dots[color]}`} />
      {showLabel && <span>Sec: {score}</span>}
      {!showLabel && <span>{score}</span>}
    </div>
  );
}
