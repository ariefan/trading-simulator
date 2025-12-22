'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { BacktestResults } from '@/components/backtesting/backtest-results';
import { api } from '@/lib/api/client';

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

interface ComparisonResult {
  strategy_id: string;
  strategy_name: string;
  final_balance: number;
  total_return_percent: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  error: string | null;
}

interface ComparisonResponse {
  symbol: string;
  timeframe: string;
  period: string;
  initial_balance: number;
  results: ComparisonResult[];
  conclusion: string;
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
  const [isComparing, setIsComparing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunBacktest = async () => {
    setIsRunning(true);
    setResults(null);
    setComparison(null);
    setError(null);

    try {
      const response = await api.backtests.create({
        strategyId: config.strategy,
        symbol: config.symbol,
        timeframe: config.timeframe,
        startDate: config.startDate,
        endDate: config.endDate,
        initialBalance: config.initialBalance,
        leverage: config.leverage,
      });

      // Transform API response to match BacktestResults component format
      setResults({
        metrics: {
          total_return_percent: response.metrics?.total_return_percent || 0,
          sharpe_ratio: response.metrics?.sharpe_ratio || 0,
          max_drawdown: response.metrics?.max_drawdown || 0,
          win_rate: response.metrics?.win_rate || 0,
          profit_factor: response.metrics?.profit_factor || 0,
          total_trades: response.metrics?.total_trades || 0,
          winning_trades: response.metrics?.winning_trades || 0,
          losing_trades: response.metrics?.losing_trades || 0,
          average_win: response.metrics?.average_win || 0,
          average_loss: response.metrics?.average_loss || 0,
          largest_win: response.metrics?.largest_win || 0,
          largest_loss: response.metrics?.largest_loss || 0,
        },
        equity_curve: response.equity_curve?.map((e: any) => ({
          date: e.timestamp?.split('T')[0] || e.timestamp,
          equity: e.equity,
        })) || [],
        trades: response.trades?.map((t: any) => ({
          id: t.id,
          side: t.side,
          size: t.size,
          entry_price: t.entry_price,
          exit_price: t.exit_price,
          pnl: t.pnl,
          pnl_percent: t.pnl_percent,
          entry_time: t.entry_time,
          exit_time: t.exit_time,
        })) || [],
      });
    } catch (err: any) {
      setError(err.data?.detail || err.message || 'Failed to run backtest');
    } finally {
      setIsRunning(false);
    }
  };

  const handleCompare = async () => {
    setIsComparing(true);
    setComparison(null);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/backtests/compare`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            strategy_id: config.strategy,
            symbol: config.symbol,
            timeframe: config.timeframe,
            start_date: config.startDate,
            end_date: config.endDate,
            initial_balance: config.initialBalance,
            leverage: config.leverage,
            parameters: {},
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Comparison failed');
      }

      const data: ComparisonResponse = await response.json();
      setComparison(data);
    } catch (err: any) {
      setError(err.message || 'Failed to compare strategies');
    } finally {
      setIsComparing(false);
    }
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

            <div className="space-y-2">
              <Button
                className="w-full"
                onClick={handleRunBacktest}
                disabled={isRunning || isComparing}
              >
                {isRunning ? 'Running Backtest...' : 'Run Backtest'}
              </Button>

              <Button
                className="w-full"
                variant="secondary"
                onClick={handleCompare}
                disabled={isRunning || isComparing}
              >
                {isComparing ? 'Comparing...' : 'Compare with Random & Buy-and-Hold'}
              </Button>
            </div>

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300 text-sm">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Comparison Results */}
          {comparison && (
            <Card>
              <CardHeader>
                <CardTitle>Strategy Comparison</CardTitle>
                <CardDescription>
                  {comparison.period} on {comparison.symbol}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Comparison Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 font-medium">Strategy</th>
                        <th className="text-right py-2 font-medium">Return</th>
                        <th className="text-right py-2 font-medium">Sharpe</th>
                        <th className="text-right py-2 font-medium">Max DD</th>
                        <th className="text-right py-2 font-medium">Win Rate</th>
                        <th className="text-right py-2 font-medium">Trades</th>
                      </tr>
                    </thead>
                    <tbody>
                      {comparison.results.map((result, idx) => (
                        <tr
                          key={result.strategy_id}
                          className={`border-b ${
                            result.strategy_id === config.strategy
                              ? 'bg-primary/5 font-medium'
                              : ''
                          }`}
                        >
                          <td className="py-2">
                            {idx === 0 && '🏆 '}
                            {result.strategy_name}
                          </td>
                          <td
                            className={`text-right py-2 ${
                              result.total_return_percent >= 0
                                ? 'text-green-600'
                                : 'text-red-600'
                            }`}
                          >
                            {result.total_return_percent >= 0 ? '+' : ''}
                            {result.total_return_percent.toFixed(2)}%
                          </td>
                          <td className="text-right py-2">
                            {result.sharpe_ratio.toFixed(2)}
                          </td>
                          <td className="text-right py-2 text-red-600">
                            -{result.max_drawdown.toFixed(2)}%
                          </td>
                          <td className="text-right py-2">
                            {result.win_rate.toFixed(1)}%
                          </td>
                          <td className="text-right py-2">{result.total_trades}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Conclusion */}
                <div
                  className={`p-4 rounded-md ${
                    comparison.conclusion.includes('LOST')
                      ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                      : 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                  }`}
                >
                  <p className="font-medium mb-1">Reality Check</p>
                  <p className="text-sm">{comparison.conclusion}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Backtest Results */}
          {results ? (
            <BacktestResults results={results} config={config} />
          ) : !comparison ? (
            <Card className="h-full flex items-center justify-center min-h-[400px]">
              <CardContent className="text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold mb-2">No Results Yet</h3>
                <p className="text-muted-foreground">
                  Configure your backtest parameters and click "Run Backtest" to see results.
                </p>
                <p className="text-muted-foreground mt-2 text-sm">
                  Or click "Compare with Random & Buy-and-Hold" to see if your strategy
                  actually works.
                </p>
              </CardContent>
            </Card>
          ) : null}
        </div>
      </div>
    </div>
  );
}
