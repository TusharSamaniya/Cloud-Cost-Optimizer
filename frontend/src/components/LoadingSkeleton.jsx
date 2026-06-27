export default function LoadingSkeleton({ className = "h-32 w-full rounded-xl" }) {
  return (
    <div className={`animate-pulse bg-gray-200 dark:bg-gray-800 ${className}`}></div>
  );
}