'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { BacktestResults } from '@/components/backtesting/backtest-results';

const CURRENCY_PAIRS = [
  { value: 'EURUSD', label: 'EUR/USD' },
  { value: 'GBPUSD', label: 'GBP/USD' },
  { value: 'USDJPY', label: 'USD/JPY' },
  { value: 'USDCHF', label: 'USD/CHF' },
  { value: 'AUDUSD', label: 'AUD/USD' },
  { value: 'USDCAD', label: 'USD/CAD' },
  { value: 'NZDUSD', label: 'NZD/USD' },
];

const TIMEFRAMES = [
  { value: '1M', label: '1 Minute' },
  { value: '5M', label: '5 Minutes' },
  { value: '15M', label: '15 Minutes' },
  { value: '1H', label: '1 Hour' },
  { value: '4H', label: '4 Hours' },
  { value: '1D', label: '1 Day' },
];

const STRATEGIES = [
  { value: 'sma-crossover', label: 'SMA Crossover' },
  { value: 'rsi-overbought', label: 'RSI Overbought/Oversold' },
  { value: 'macd-signal', label: 'MACD Signal' },
  { value: 'custom', label: 'Custom Strategy' },
];

interface BacktestConfig {
  strategy: string;
  symbol: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  initialBalance: number;
  leverage: number;
}

export default function BacktestingPage() {
  const [config, setConfig] = useState<BacktestConfig>({
    strategy: 'sma-crossover',
    symbol: 'EURUSD',
    timeframe: '1H',
    startDate: '2023-01-01',
    endDate: '2023-12-31',
    initialBalance: 100000,
    leverage: 100,
  });

  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRunBacktest = async () => {
    setIsRunning(true);
    setResults(null);

    // Simulate backtest (replace with actual API call)
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock results
    setResults({
      metrics: {
        total_return_percent: 15.5,
        sharpe_ratio: 1.85,
        max_drawdown: 8.2,
        win_rate: 58.3,
        profit_factor: 1.72,
        total_trades: 124,
        winning_trades: 72,
        losing_trades: 52,
        average_win: 285.50,
        average_loss: -165.30,
        largest_win: 1250.00,
        largest_loss: -520.00,
      },
      equity_curve: generateMockEquityCurve(config.initialBalance),
      trades: generateMockTrades(),
    });

    setIsRunning(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Backtesting</h1>
        <p className="text-muted-foreground">
          Test your trading strategies on historical data
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Configuration Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Set up your backtest parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Strategy */}
            <div className="space-y-2">
              <Label htmlFor="strategy">Strategy</Label>
              <select
                id="strategy"
                value={config.strategy}
                onChange={(e) => setConfig({ ...config, strategy: e.target.value })}
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                {STRATEGIES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Symbol */}
            <div className="space-y-2">
              <Label htmlFor="symbol">Currency Pair</Label>
              <select
                id="symbol"
                value={config.symbol}
                onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                {CURRENCY_PAIRS.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Timeframe */}
            <div className="space-y-2">
              <Label htmlFor="timeframe">Timeframe</Label>
              <select
                id="timeframe"
                value={config.timeframe}
                onChange={(e) => setConfig({ ...config, timeframe: e.target.value })}
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                {TIMEFRAMES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={config.startDate}
                  onChange={(e) => setConfig({ ...config, startDate: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endDate">End Date</Label>
                <Input
                  id="endDate"
                  type="date"
                  value={config.endDate}
                  onChange={(e) => setConfig({ ...config, endDate: e.target.value })}
                />
              </div>
            </div>

            {/* Initial Balance */}
            <div className="space-y-2">
              <Label htmlFor="balance">Initial Balance ($)</Label>
              <Input
                id="balance"
                type="number"
                value={config.initialBalance}
                onChange={(e) =>
                  setConfig({ ...config, initialBalance: Number(e.target.value) })
                }
              />
            </div>

            {/* Leverage */}
            <div className="space-y-2">
              <Label htmlFor="leverage">Leverage</Label>
              <select
                id="leverage"
                value={config.leverage}
                onChange={(e) => setConfig({ ...config, leverage: Number(e.target.value) })}
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                <option value={10}>1:10</option>
                <option value={50}>1:50</option>
                <option value={100}>1:100</option>
                <option value={200}>1:200</option>
                <option value={500}>1:500</option>
              </select>
            </div>

            <Button
              className="w-full"
              onClick={handleRunBacktest}
              disabled={isRunning}
            >
              {isRunning ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Running Backtest...
                </>
              ) : (
                'Run Backtest'
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          {results ? (
            <BacktestResults results={results} config={config} />
          ) : (
            <Card className="h-full flex items-center justify-center min-h-[400px]">
              <CardContent className="text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold mb-2">No Results Yet</h3>
                <p className="text-muted-foreground">
                  Configure your backtest parameters and click "Run Backtest" to see results.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// Helper functions to generate mock data
function generateMockEquityCurve(initialBalance: number) {
  const points = [];
  let equity = initialBalance;
  const startDate = new Date('2023-01-01');

  for (let i = 0; i < 365; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);

    // Random walk with slight upward bias
    const change = (Math.random() - 0.48) * 0.02 * equity;
    equity += change;

    points.push({
      date: date.toISOString().split('T')[0],
      equity: Math.round(equity * 100) / 100,
    });
  }

  return points;
}

function generateMockTrades() {
  const trades = [];
  const sides = ['long', 'short'];

  for (let i = 0; i < 20; i++) {
    const side = sides[Math.floor(Math.random() * 2)];
    const pnl = (Math.random() - 0.4) * 500;

    trades.push({
      id: `trade-${i + 1}`,
      side,
      size: 0.1,
      entry_price: 1.1 + Math.random() * 0.01,
      exit_price: 1.1 + Math.random() * 0.01,
      pnl: Math.round(pnl * 100) / 100,
      pnl_percent: Math.round((pnl / 1000) * 10000) / 100,
      entry_time: new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString(),
      exit_time: new Date(2023, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString(),
    });
  }

  return trades;
}
