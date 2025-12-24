'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: '🏠' },
  { name: 'Backtesting', href: '/backtesting', icon: '📊' },
  { name: 'Strategies', href: '/strategies', icon: '📈' },
  { name: 'Trading', href: '/trading', icon: '💹' },
  { name: 'Portfolio', href: '/portfolio', icon: '💼' },
  { name: 'History', href: '/history', icon: '📜' },
  { name: 'AI Assistant', href: '/assistant', icon: '🤖' },
];

const bottomNav = [
  { name: 'Settings', href: '/settings', icon: '⚙️' },
  { name: 'Help', href: '/help', icon: '❓' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow border-r bg-card pt-5 overflow-y-auto">
        {/* Logo */}
        <div className="flex items-center flex-shrink-0 px-4 mb-5">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">📈</span>
            <span className="font-bold text-lg">Forex Simulator</span>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 px-2 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Bottom Navigation */}
        <div className="flex-shrink-0 border-t p-2">
          {bottomNav.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
