'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MiniChart } from '@/components/charts/candlestick-chart';
import { formatCurrency, formatPercentage } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface PortfolioData {
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  margin_level: number | null;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  total_pnl_percent: number;
}

interface PortfolioSnapshot {
  timestamp: string;
  balance: number;
  equity: number;
}

interface PerformanceMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  profit_factor: number;
  average_win: number;
  average_loss: number;
  largest_win: number;
  largest_loss: number;
  average_trade: number;
  total_pnl: number;
  sharpe_ratio: number;
  max_drawdown: number;
}

interface AllocationItem {
  symbol: string;
  side: string;
  size: number;
  margin_used: number;
  unrealized_pnl: number;
  allocation_percent: number;
}

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [history, setHistory] = useState<PortfolioSnapshot[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [allocation, setAllocation] = useState<AllocationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [portfolioRes, historyRes, metricsRes, allocationRes] = await Promise.all([
          fetch(`${API_BASE_URL}/api/v1/portfolio/`),
          fetch(`${API_BASE_URL}/api/v1/portfolio/history?days=30`),
          fetch(`${API_BASE_URL}/api/v1/portfolio/metrics`),
          fetch(`${API_BASE_URL}/api/v1/portfolio/allocation`),
        ]);

        if (!portfolioRes.ok) throw new Error('Failed to fetch portfolio');
        if (!historyRes.ok) throw new Error('Failed to fetch history');
        if (!metricsRes.ok) throw new Error('Failed to fetch metrics');
        if (!allocationRes.ok) throw new Error('Failed to fetch allocation');

        const [portfolioData, historyData, metricsData, allocationData] = await Promise.all([
          portfolioRes.json(),
          historyRes.json(),
          metricsRes.json(),
          allocationRes.json(),
        ]);

        setPortfolio(portfolioData);
        setHistory(historyData);
        setMetrics(metricsData);
        setAllocation(allocationData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load portfolio data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Convert history to chart format
  const equityChartData = history.map((snapshot) => {
    const date = new Date(snapshot.timestamp);
    return {
      time: date.toISOString().slice(0, 10),
      open: snapshot.equity,
      high: snapshot.equity * 1.001,
      low: snapshot.equity * 0.999,
      close: snapshot.equity,
    };
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Portfolio</h1>
          <p className="text-muted-foreground">
            Track your trading performance and portfolio allocation
          </p>
        </div>
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-500">Error: {error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Make sure the API server is running at {API_BASE_URL}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const isPositive = (portfolio?.total_pnl || 0) >= 0;

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
            <p className="text-2xl font-bold">{formatCurrency(portfolio?.balance || 0)}</p>
            <p className="text-sm text-muted-foreground">
              Realized P&L: <span className={portfolio?.realized_pnl && portfolio.realized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                {portfolio?.realized_pnl && portfolio.realized_pnl >= 0 ? '+' : ''}{formatCurrency(portfolio?.realized_pnl || 0)}
              </span>
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Equity</p>
            <p className="text-2xl font-bold">{formatCurrency(portfolio?.equity || 0)}</p>
            <p className="text-sm text-muted-foreground">
              Floating P&L: <span className={portfolio?.unrealized_pnl && portfolio.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                {portfolio?.unrealized_pnl && portfolio.unrealized_pnl >= 0 ? '+' : ''}{formatCurrency(portfolio?.unrealized_pnl || 0)}
              </span>
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Free Margin</p>
            <p className="text-2xl font-bold">{formatCurrency(portfolio?.free_margin || 0)}</p>
            <p className="text-sm text-muted-foreground">
              Used: {formatCurrency(portfolio?.margin || 0)}
              {portfolio?.margin_level && ` (${portfolio.margin_level.toFixed(0)}%)`}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total P&L</p>
            <p className={`text-2xl font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{formatCurrency(portfolio?.total_pnl || 0)}
            </p>
            <p className="text-sm text-muted-foreground">
              {isPositive ? '+' : ''}{formatPercentage(portfolio?.total_pnl_percent || 0)}
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
            {equityChartData.length > 0 ? (
              <MiniChart data={equityChartData} height={192} isPositive={isPositive} />
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                No historical data available
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Performance Summary */}
        <Card>
          <CardHeader>
            <CardTitle>Trade Summary</CardTitle>
            <CardDescription>Win/Loss statistics</CardDescription>
          </CardHeader>
          <CardContent>
            {metrics && metrics.total_trades > 0 ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Total Trades</span>
                  <span className="font-bold">{metrics.total_trades}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Winning Trades</span>
                  <span className="font-bold text-green-600">{metrics.winning_trades}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Losing Trades</span>
                  <span className="font-bold text-red-600">{metrics.losing_trades}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Win Rate</span>
                  <span className="font-bold">{metrics.win_rate.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Average Win</span>
                  <span className="font-bold text-green-600">+{formatCurrency(metrics.average_win)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Average Loss</span>
                  <span className="font-bold text-red-600">-{formatCurrency(metrics.average_loss)}</span>
                </div>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No trades yet. Start trading to see statistics.
              </div>
            )}
          </CardContent>
        </Card>

        {/* Currency Allocation */}
        <Card>
          <CardHeader>
            <CardTitle>Position Allocation</CardTitle>
            <CardDescription>Current open positions by margin usage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {allocation.length > 0 ? (
              allocation.map((item) => (
                <div key={`${item.symbol}-${item.side}`} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">
                      {item.symbol} <span className={`text-xs ${item.side === 'long' ? 'text-green-600' : 'text-red-600'}`}>
                        ({item.side.toUpperCase()})
                      </span>
                    </span>
                    <div className="flex items-center gap-4">
                      <span
                        className={`text-sm font-medium ${
                          item.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {item.unrealized_pnl >= 0 ? '+' : ''}
                        {formatCurrency(item.unrealized_pnl)}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {item.allocation_percent.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        item.unrealized_pnl >= 0 ? 'bg-green-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${item.allocation_percent}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No open positions. Open a trade to see allocation.
              </div>
            )}
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
              <p className="text-2xl font-bold">{metrics?.total_trades || 0}</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <p className="text-2xl font-bold">{(metrics?.win_rate || 0).toFixed(1)}%</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Profit Factor</p>
              <p className="text-2xl font-bold">{(metrics?.profit_factor || 0).toFixed(2)}</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Average Trade</p>
              <p className={`text-2xl font-bold ${(metrics?.average_trade || 0) >= 0 ? '' : 'text-red-600'}`}>
                {(metrics?.average_trade || 0) >= 0 ? '+' : ''}{formatCurrency(metrics?.average_trade || 0)}
              </p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
              <p className="text-2xl font-bold">{(metrics?.sharpe_ratio || 0).toFixed(2)}</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Max Drawdown</p>
              <p className="text-2xl font-bold text-red-600">-{(metrics?.max_drawdown || 0).toFixed(2)}%</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Largest Win</p>
              <p className="text-2xl font-bold text-green-600">+{formatCurrency(metrics?.largest_win || 0)}</p>
            </div>
            <div className="space-y-1 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">Largest Loss</p>
              <p className="text-2xl font-bold text-red-600">{formatCurrency(metrics?.largest_loss || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
