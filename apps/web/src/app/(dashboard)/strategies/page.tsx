'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StrategyParameter {
  name: string;
  type: string;
  default: any;
  min?: number;
  max?: number;
  description: string;
}

interface Strategy {
  id: string;
  name: string;
  description: string;
  code: string;
  parameters: StrategyParameter[];
  created_at: string;
  updated_at: string;
}

interface StrategyTemplate {
  name: string;
  description: string;
  code: string;
  parameters: StrategyParameter[];
}

export default function StrategiesPage() {
  const router = useRouter();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [templates, setTemplates] = useState<StrategyTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isEditing, setIsEditing] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    description: '',
    code: '',
  });

  // Fetch strategies and templates on mount
  useEffect(() => {
    fetchStrategies();
    fetchTemplates();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/strategies`);
      if (response.ok) {
        const data = await response.json();
        setStrategies(data.strategies || []);
      }
    } catch (err) {
      console.error('Failed to fetch strategies:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/strategies/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
        if (data.templates?.length > 0) {
          setNewStrategy((prev) => ({
            ...prev,
            code: data.templates[0].code,
          }));
        }
      }
    } catch (err) {
      console.error('Failed to fetch templates:', err);
    }
  };

  const handleCreateStrategy = async () => {
    if (!newStrategy.name.trim()) {
      setError('Strategy name is required');
      return;
    }
    if (!newStrategy.code.trim() || newStrategy.code.length < 10) {
      setError('Strategy code must be at least 10 characters');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/strategies`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newStrategy.name,
          description: newStrategy.description,
          code: newStrategy.code,
          parameters: [],
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create strategy');
      }

      const created = await response.json();
      setStrategies((prev) => [created, ...prev]);
      setIsCreating(false);
      setNewStrategy({
        name: '',
        description: '',
        code: templates[0]?.code || '',
      });
    } catch (err: any) {
      setError(err.message || 'Failed to create strategy');
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateStrategy = async (id: string) => {
    const strategy = strategies.find((s) => s.id === id);
    if (!strategy) return;

    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/strategies/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: strategy.name,
          description: strategy.description,
          code: strategy.code,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update strategy');
      }

      const updated = await response.json();
      setStrategies((prev) =>
        prev.map((s) => (s.id === id ? updated : s))
      );
      setIsEditing(null);
    } catch (err: any) {
      setError(err.message || 'Failed to update strategy');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteStrategy = async (id: string) => {
    if (!confirm('Are you sure you want to delete this strategy?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/strategies/${id}`, {
        method: 'DELETE',
      });

      if (response.ok || response.status === 204) {
        setStrategies((prev) => prev.filter((s) => s.id !== id));
      }
    } catch (err) {
      console.error('Failed to delete strategy:', err);
    }
  };

  const handleBacktest = (strategyId: string) => {
    // Navigate to backtesting page with strategy pre-selected
    router.push(`/backtesting?strategy=${strategyId}`);
  };

  const updateEditingStrategy = (id: string, field: string, value: string) => {
    setStrategies((prev) =>
      prev.map((s) => (s.id === id ? { ...s, [field]: value } : s))
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading strategies...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Trading Strategies</h1>
          <p className="text-muted-foreground">
            Create and manage your custom trading strategies
          </p>
        </div>
        <Button onClick={() => setIsCreating(true)} disabled={isCreating}>
          Create Strategy
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300 text-sm">
          {error}
          <button
            className="ml-2 underline"
            onClick={() => setError(null)}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Create Strategy Form */}
      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Strategy</CardTitle>
            <CardDescription>
              Define your trading strategy using Python code
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Strategy Name *</Label>
                <Input
                  id="name"
                  placeholder="My Strategy"
                  value={newStrategy.name}
                  onChange={(e) =>
                    setNewStrategy({ ...newStrategy, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template">Start from Template</Label>
                <select
                  id="template"
                  value={selectedTemplate}
                  onChange={(e) => {
                    const idx = Number(e.target.value);
                    setSelectedTemplate(idx);
                    if (templates[idx]) {
                      setNewStrategy({
                        ...newStrategy,
                        code: templates[idx].code,
                      });
                    }
                  }}
                  className="w-full h-10 px-3 rounded-md border border-input bg-background"
                >
                  {templates.map((t, i) => (
                    <option key={i} value={i}>
                      {t.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Brief description of your strategy"
                value={newStrategy.description}
                onChange={(e) =>
                  setNewStrategy({ ...newStrategy, description: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <Label>Strategy Code *</Label>
              <div className="relative">
                <textarea
                  value={newStrategy.code}
                  onChange={(e) =>
                    setNewStrategy({ ...newStrategy, code: e.target.value })
                  }
                  className="w-full h-96 p-4 font-mono text-sm rounded-md border border-input bg-muted/50 resize-none"
                  spellCheck={false}
                  placeholder="class MyStrategy(Strategy):&#10;    def init(self):&#10;        pass&#10;&#10;    def next(self):&#10;        pass"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Define your strategy by extending the Strategy base class. Use init() to set up
                indicators and next() to define trading logic.
              </p>
            </div>

            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setIsCreating(false);
                  setError(null);
                }}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button onClick={handleCreateStrategy} disabled={isSaving}>
                {isSaving ? 'Creating...' : 'Create Strategy'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Strategy List */}
      <div className="grid gap-4">
        {strategies.map((strategy) => (
          <Card key={strategy.id}>
            <CardContent className="pt-6">
              {isEditing === strategy.id ? (
                // Edit Mode
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Name</Label>
                      <Input
                        value={strategy.name}
                        onChange={(e) =>
                          updateEditingStrategy(strategy.id, 'name', e.target.value)
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Description</Label>
                      <Input
                        value={strategy.description}
                        onChange={(e) =>
                          updateEditingStrategy(strategy.id, 'description', e.target.value)
                        }
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Code</Label>
                    <textarea
                      value={strategy.code}
                      onChange={(e) =>
                        updateEditingStrategy(strategy.id, 'code', e.target.value)
                      }
                      className="w-full h-80 p-4 font-mono text-sm rounded-md border border-input bg-muted/50 resize-none"
                      spellCheck={false}
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setIsEditing(null);
                        fetchStrategies(); // Reset to original
                      }}
                      disabled={isSaving}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={() => handleUpdateStrategy(strategy.id)}
                      disabled={isSaving}
                    >
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </Button>
                  </div>
                </div>
              ) : (
                // View Mode
                <div className="flex items-start justify-between">
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold">{strategy.name}</h3>
                      <span className="px-2 py-0.5 text-xs rounded-full bg-muted">
                        Custom
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {strategy.description || 'No description'}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Created: {new Date(strategy.created_at).toLocaleDateString()}
                      {strategy.updated_at !== strategy.created_at && (
                        <> · Updated: {new Date(strategy.updated_at).toLocaleDateString()}</>
                      )}
                    </p>
                    {/* Code Preview */}
                    <details className="mt-2">
                      <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                        View code
                      </summary>
                      <pre className="mt-2 p-3 text-xs bg-muted/50 rounded-md overflow-x-auto max-h-40">
                        <code>{strategy.code}</code>
                      </pre>
                    </details>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditing(strategy.id)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteStrategy(strategy.id)}
                    >
                      Delete
                    </Button>
                    <Button size="sm" onClick={() => handleBacktest(strategy.id)}>
                      Backtest
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {strategies.length === 0 && !isCreating && (
        <Card className="py-12">
          <CardContent className="text-center">
            <div className="text-6xl mb-4">📈</div>
            <h3 className="text-xl font-semibold mb-2">No Strategies Yet</h3>
            <p className="text-muted-foreground mb-4">
              Create your first custom trading strategy to get started
            </p>
            <Button onClick={() => setIsCreating(true)}>Create Strategy</Button>
          </CardContent>
        </Card>
      )}

      {/* Strategy Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Strategy Reference</CardTitle>
          <CardDescription>
            Available indicators and methods for your strategies
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <h4 className="font-semibold mb-2">Available Indicators</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li><code className="text-primary">SMA(data, period)</code> - Simple Moving Average</li>
                <li><code className="text-primary">EMA(data, period)</code> - Exponential Moving Average</li>
                <li><code className="text-primary">RSI(data, period)</code> - Relative Strength Index</li>
                <li><code className="text-primary">MACD(data, fast, slow, signal)</code> - MACD</li>
                <li><code className="text-primary">BOLLINGER_BANDS(data, period, std)</code> - Bollinger Bands</li>
                <li><code className="text-primary">ATR(high, low, close, period)</code> - Average True Range</li>
                <li><code className="text-primary">STOCHASTIC(high, low, close, k, d)</code> - Stochastic</li>
                <li><code className="text-primary">ADX(high, low, close, period)</code> - ADX</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Trading Methods</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li><code className="text-primary">self.buy(size, sl, tp)</code> - Open long position</li>
                <li><code className="text-primary">self.sell(size, sl, tp)</code> - Open short / close long</li>
                <li><code className="text-primary">self.close()</code> - Close current position</li>
                <li><code className="text-primary">self.position</code> - Current position size</li>
                <li><code className="text-primary">self.data['close']</code> - Close price series</li>
                <li><code className="text-primary">self.data['open/high/low']</code> - OHLC data</li>
                <li><code className="text-primary">crossover(a, b)</code> - True when a crosses above b</li>
                <li><code className="text-primary">self.I(indicator, ...args)</code> - Register indicator</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
