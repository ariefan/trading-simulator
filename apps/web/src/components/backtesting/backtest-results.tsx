'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface BacktestResultsProps {
  results: {
    metrics: {
      total_return_percent: number;
      sharpe_ratio: number;
      max_drawdown: number;
      win_rate: number;
      profit_factor: number;
      total_trades: number;
      winning_trades: number;
      losing_trades: number;
      average_win: number;
      average_loss: number;
      largest_win: number;
      largest_loss: number;
    };
    equity_curve: Array<{ date: string; equity: number }>;
    trades: Array<{
      id: string;
      side: string;
      size: number;
      entry_price: number;
      exit_price: number;
      pnl: number;
      pnl_percent: number;
      entry_time: string;
      exit_time: string;
    }>;
  };
  config: {
    symbol: string;
    timeframe: string;
    startDate: string;
    endDate: string;
    initialBalance: number;
  };
}

export function BacktestResults({ results, config }: BacktestResultsProps) {
  const { metrics, equity_curve, trades } = results;
  const finalEquity = equity_curve[equity_curve.length - 1]?.equity || config.initialBalance;
  const totalReturn = finalEquity - config.initialBalance;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard
          title="Total Return"
          value={formatCurrency(totalReturn)}
          subValue={formatPercentage(metrics.total_return_percent)}
          trend={totalReturn >= 0 ? 'up' : 'down'}
        />
        <MetricCard
          title="Sharpe Ratio"
          value={metrics.sharpe_ratio.toFixed(2)}
          subValue={getSharpeRating(metrics.sharpe_ratio)}
        />
        <MetricCard
          title="Max Drawdown"
          value={formatPercentage(-metrics.max_drawdown)}
          trend="down"
        />
        <MetricCard
          title="Win Rate"
          value={formatPercentage(metrics.win_rate)}
          subValue={`${metrics.winning_trades}/${metrics.total_trades} trades`}
        />
      </div>

      {/* Equity Curve */}
      <Card>
        <CardHeader>
          <CardTitle>Equity Curve</CardTitle>
          <CardDescription>
            Account balance over time for {config.symbol} ({config.timeframe})
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-muted/50 rounded-lg">
            <EquityChart data={equity_curve} initialBalance={config.initialBalance} />
          </div>
        </CardContent>
      </Card>

      {/* Detailed Metrics */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <MetricRow label="Total Trades" value={metrics.total_trades.toString()} />
            <MetricRow label="Winning Trades" value={metrics.winning_trades.toString()} />
            <MetricRow label="Losing Trades" value={metrics.losing_trades.toString()} />
            <Separator />
            <MetricRow label="Profit Factor" value={metrics.profit_factor.toFixed(2)} />
            <MetricRow label="Average Win" value={formatCurrency(metrics.average_win)} />
            <MetricRow
              label="Average Loss"
              value={formatCurrency(metrics.average_loss)}
            />
            <Separator />
            <MetricRow label="Largest Win" value={formatCurrency(metrics.largest_win)} />
            <MetricRow
              label="Largest Loss"
              value={formatCurrency(metrics.largest_loss)}
            />
          </CardContent>
        </Card>

        {/* Recent Trades */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Trades</CardTitle>
            <CardDescription>Last 10 trades from backtest</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {trades.slice(0, 10).map((trade) => (
                <div
                  key={trade.id}
                  className="flex items-center justify-between p-2 rounded bg-muted/50"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 text-xs rounded ${
                        trade.side === 'long'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                          : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                      }`}
                    >
                      {trade.side.toUpperCase()}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {trade.size} lots
                    </span>
                  </div>
                  <span
                    className={`font-medium ${
                      trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {trade.pnl >= 0 ? '+' : ''}
                    {formatCurrency(trade.pnl)}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  subValue,
  trend,
}: {
  title: string;
  value: string;
  subValue?: string;
  trend?: 'up' | 'down';
}) {
  const trendColor =
    trend === 'up'
      ? 'text-green-600'
      : trend === 'down'
      ? 'text-red-600'
      : 'text-foreground';

  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm text-muted-foreground">{title}</p>
        <p className={`text-2xl font-bold ${trendColor}`}>{value}</p>
        {subValue && (
          <p className="text-sm text-muted-foreground">{subValue}</p>
        )}
      </CardContent>
    </Card>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function getSharpeRating(sharpe: number): string {
  if (sharpe >= 3) return 'Excellent';
  if (sharpe >= 2) return 'Very Good';
  if (sharpe >= 1) return 'Good';
  if (sharpe >= 0) return 'Acceptable';
  return 'Poor';
}

function EquityChart({
  data,
  initialBalance,
}: {
  data: Array<{ date: string; equity: number }>;
  initialBalance: number;
}) {
  if (data.length === 0) return <p>No data available</p>;

  const maxEquity = Math.max(...data.map((d) => d.equity));
  const minEquity = Math.min(...data.map((d) => d.equity));
  const range = maxEquity - minEquity || 1;

  // Create a simple SVG chart
  const width = 800;
  const height = 200;
  const padding = 40;

  const xScale = (i: number) => padding + (i / (data.length - 1)) * (width - 2 * padding);
  const yScale = (val: number) =>
    height - padding - ((val - minEquity) / range) * (height - 2 * padding);

  const pathData = data
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i)} ${yScale(d.equity)}`)
    .join(' ');

  const finalEquity = data[data.length - 1].equity;
  const isProfit = finalEquity >= initialBalance;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
        const y = padding + pct * (height - 2 * padding);
        return (
          <line
            key={pct}
            x1={padding}
            y1={y}
            x2={width - padding}
            y2={y}
            stroke="currentColor"
            strokeOpacity={0.1}
          />
        );
      })}

      {/* Initial balance line */}
      <line
        x1={padding}
        y1={yScale(initialBalance)}
        x2={width - padding}
        y2={yScale(initialBalance)}
        stroke="currentColor"
        strokeOpacity={0.3}
        strokeDasharray="5,5"
      />

      {/* Equity curve */}
      <path
        d={pathData}
        fill="none"
        stroke={isProfit ? '#22c55e' : '#ef4444'}
        strokeWidth={2}
      />

      {/* Labels */}
      <text x={padding} y={height - 10} className="text-xs fill-current opacity-50">
        {data[0].date}
      </text>
      <text
        x={width - padding}
        y={height - 10}
        textAnchor="end"
        className="text-xs fill-current opacity-50"
      >
        {data[data.length - 1].date}
      </text>
    </svg>
  );
}
