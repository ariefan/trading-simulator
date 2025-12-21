'use client';

import { signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  user?: {
    name?: string | null;
    email?: string | null;
    image?: string | null;
  } | null;
}

export function Header({ user }: HeaderProps) {
  return (
    <header className="border-b bg-card">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left side - can add breadcrumbs or page title */}
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-muted-foreground">
            Educational Trading Platform
          </h2>
        </div>

        {/* Right side - user menu */}
        <div className="flex items-center gap-4">
          {/* Balance Display */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-muted rounded-md">
            <span className="text-sm text-muted-foreground">Balance:</span>
            <span className="text-sm font-semibold">$100,000.00</span>
          </div>

          {/* User Info */}
          <div className="flex items-center gap-3">
            {user?.image ? (
              <img
                src={user.image}
                alt={user.name || 'User'}
                className="h-8 w-8 rounded-full"
              />
            ) : (
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-medium">
                {user?.name?.charAt(0) || 'U'}
              </div>
            )}
            <div className="hidden sm:block">
              <p className="text-sm font-medium">{user?.name}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
          </div>

          <Button variant="ghost" size="sm" onClick={() => signOut()}>
            Sign Out
          </Button>
        </div>
      </div>
    </header>
  );
}
