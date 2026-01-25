'use client';

import { useSession } from 'next-auth/react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { BarChart2, TrendingUp, LineChart } from 'lucide-react';

export default function DashboardPage() {
  const { data: session } = useSession();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome back, {session?.user?.name?.split(' ')[0]}!
        </h1>
        <p className="text-muted-foreground">
          Your forex trading simulator dashboard
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Account Balance"
          value="$100,000.00"
          description="Virtual trading balance"
        />
        <StatCard
          title="Total P&L"
          value="$0.00"
          description="All-time profit/loss"
          trend="neutral"
        />
        <StatCard
          title="Backtests Run"
          value="0"
          description="Strategies tested"
        />
        <StatCard
          title="Win Rate"
          value="--"
          description="No trades yet"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart2 className="h-6 w-6 text-primary" />
              Backtesting
            </CardTitle>
            <CardDescription>
              Test your trading strategies on historical data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/backtesting">
              <Button className="w-full">Run Backtest</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-primary" />
              Paper Trading
            </CardTitle>
            <CardDescription>
              Practice trading with virtual money
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/trading">
              <Button variant="outline" className="w-full">
                Start Trading
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LineChart className="h-6 w-6 text-primary" />
              Strategies
            </CardTitle>
            <CardDescription>
              Create and manage trading strategies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/strategies">
              <Button variant="outline" className="w-full">
                View Strategies
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Your latest backtests and trades</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <p>No recent activity. Run your first backtest to get started!</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  title,
  value,
  description,
  trend,
}: {
  title: string;
  value: string;
  description: string;
  trend?: 'up' | 'down' | 'neutral';
}) {
  const trendColor =
    trend === 'up'
      ? 'text-green-600'
      : trend === 'down'
        ? 'text-red-600'
        : 'text-foreground';

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
        <CardTitle className={`text-2xl ${trendColor}`}>{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
