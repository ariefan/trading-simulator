'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MiniChart } from '@/components/charts/candlestick-chart';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface PortfolioStats {
  balance: number;
  equity: number;
  margin: number;
  freeMargin: number;
  marginLevel: number;
  dailyPnl: number;
  weeklyPnl: number;
  monthlyPnl: number;
  allTimePnl: number;
}

const MOCK_STATS: PortfolioStats = {
  balance: 105432.50,
  equity: 106789.25,
  margin: 2500.00,
  freeMargin: 104289.25,
  marginLevel: 4271.57,
  dailyPnl: 432.50,
  weeklyPnl: 1876.25,
  monthlyPnl: 5432.50,
  allTimePnl: 6789.25,
};

const MOCK_EQUITY_HISTORY = Array.from({ length: 30 }, (_, i) => {
  const date = new Date();
  date.setDate(date.getDate() - (30 - i));
  return {
    time: date.toISOString().slice(0, 10),
    open: 100000 + i * 200 + Math.random() * 500,
    high: 100000 + i * 200 + Math.random() * 800,
    low: 100000 + i * 200 - Math.random() * 300,
    close: 100000 + i * 200 + Math.random() * 600,
  };
});

const MOCK_MONTHLY_RETURNS = [
  { month: 'Jan', return: 2.5 },
  { month: 'Feb', return: -1.2 },
  { month: 'Mar', return: 3.8 },
  { month: 'Apr', return: 1.5 },
  { month: 'May', return: -0.8 },
  { month: 'Jun', return: 4.2 },
  { month: 'Jul', return: 2.1 },
  { month: 'Aug', return: -2.5 },
  { month: 'Sep', return: 3.2 },
  { month: 'Oct', return: 1.8 },
  { month: 'Nov', return: 2.9 },
  { month: 'Dec', return: 1.5 },
];

const MOCK_ALLOCATION = [
  { pair: 'EUR/USD', percentage: 35, pnl: 2340 },
  { pair: 'GBP/USD', percentage: 25, pnl: 1560 },
  { pair: 'USD/JPY', percentage: 20, pnl: -890 },
  { pair: 'AUD/USD', percentage: 12, pnl: 780 },
  { pair: 'USD/CHF', percentage: 8, pnl: 450 },
];

export default function PortfolioPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Portfolio</h1>
        <p className="text-muted-foreground">
          Track your trading performance and portfolio allocation
        </p>
      </div>

      {/* Account Summary */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Balance</p>
            <p className="text-2xl font-bold">{formatCurrency(MOCK_STATS.balance)}</p>
            <p className="text-sm text-green-600">
              +{formatCurrency(MOCK_STATS.dailyPnl)} today
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Equity</p>
            <p className="text-2xl font-bold">{formatCurrency(MOCK_STATS.equity)}</p>
            <p className="text-sm text-muted-foreground">
              Floating P&L: {formatCurrency(MOCK_STATS.equity - MOCK_STATS.balance)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Free Margin</p>
            <p className="text-2xl font-bold">{formatCurrency(MOCK_STATS.freeMargin)}</p>
            <p className="text-sm text-muted-foreground">
              Used: {formatCurrency(MOCK_STATS.margin)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">All-Time P&L</p>
            <p className="text-2xl font-bold text-green-600">
              +{formatCurrency(MOCK_STATS.allTimePnl)}
            </p>
            <p className="text-sm text-muted-foreground">
              +{formatPercentage((MOCK_STATS.allTimePnl / 100000) * 100)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Equity Curve */}
      <Card>
        <CardHeader>
          <CardTitle>Equity Curve</CardTitle>
          <CardDescription>Account equity over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-48">
            <MiniChart data={MOCK_EQUITY_HISTORY} height={192} isPositive />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Monthly Returns */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Returns</CardTitle>
            <CardDescription>Performance by month (2024)</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-2">
              {MOCK_MONTHLY_RETURNS.map((item) => (
                <div
                  key={item.month}
                  className={`p-3 rounded-md text-center ${
                    item.return >= 0 ? 'bg-green-100 dark:bg-green-900/30' : 'bg-red-100 dark:bg-red-900/30'
                  }`}
                >
                  <p className="text-xs text-muted-foreground">{item.month}</p>
                  <p
                    className={`font-semibold ${
                      item.return >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {item.return >= 0 ? '+' : ''}
                    {item.return.toFixed(1)}%
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Currency Allocation */}
        <Card>
          <CardHeader>
            <CardTitle>Currency Allocation</CardTitle>
            <CardDescription>Trading activity by currency pair</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {MOCK_ALLOCATION.map((item) => (
              <div key={item.pair} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.pair}</span>
                  <div className="flex items-center gap-4">
                    <span
                      className={`text-sm font-medium ${
                        item.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {item.pnl >= 0 ? '+' : ''}
                      {formatCurrency(item.pnl)}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {item.percentage}%
                    </span>
                  </div>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.pnl >= 0 ? 'bg-green-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Metrics</CardTitle>
          <CardDescription>Key performance indicators</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Total Trades</p>
              <p className="text-2xl font-bold">247</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <p className="text-2xl font-bold">58.3%</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Profit Factor</p>
              <p className="text-2xl font-bold">1.72</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Avg Trade Duration</p>
              <p className="text-2xl font-bold">4.2h</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
              <p className="text-2xl font-bold">1.85</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Max Drawdown</p>
              <p className="text-2xl font-bold text-red-600">-8.2%</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Best Trade</p>
              <p className="text-2xl font-bold text-green-600">+$1,250</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Worst Trade</p>
              <p className="text-2xl font-bold text-red-600">-$520</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
