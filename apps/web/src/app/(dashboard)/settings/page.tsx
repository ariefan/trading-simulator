'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { api, UserSettings, UserProfile } from '@/lib/api/client';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    defaultLeverage: 100,
    defaultLotSize: 0.1,
    riskPerTrade: 2,
    currency: 'USD',
    timezone: 'UTC',
    theme: 'dark',
    emailNotifications: true,
    tradeAlerts: true,
  });
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Get token from localStorage
  const getToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  };

  // Load settings from backend
  useEffect(() => {
    const loadData = async () => {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const [userSettings, userProfile] = await Promise.all([
          api.users.getSettings(token),
          api.users.getProfile(token),
        ]);

        setSettings((prev) => ({
          ...prev,
          defaultLeverage: userSettings.default_leverage,
          defaultLotSize: userSettings.default_lot_size,
          theme: userSettings.theme,
          emailNotifications: userSettings.notifications_enabled,
          tradeAlerts: userSettings.notifications_enabled,
        }));
        setProfile(userProfile);
      } catch (error) {
        console.error('Failed to load settings:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleSave = async () => {
    const token = getToken();
    if (!token) {
      setMessage({ type: 'error', text: 'Not authenticated. Please log in again.' });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      const userSettings: UserSettings = {
        default_leverage: settings.defaultLeverage,
        default_lot_size: settings.defaultLotSize,
        theme: settings.theme,
        notifications_enabled: settings.emailNotifications,
      };

      await api.users.updateSettings(token, userSettings);
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (error) {
      console.error('Failed to save settings:', error);
      setMessage({ type: 'error', text: 'Failed to save settings. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset your paper trading account? This will reset your balance to $100,000 and clear all trade history.')) {
      return;
    }

    setResetting(true);
    setMessage(null);

    try {
      await api.trading.reset();
      setMessage({ type: 'success', text: 'Account reset successfully! Your balance is now $100,000.' });
    } catch (error) {
      console.error('Failed to reset account:', error);
      setMessage({ type: 'error', text: 'Failed to reset account. Please try again.' });
    } finally {
      setResetting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 max-w-3xl">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your trading preferences and account settings
        </p>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-500/10 text-green-500 border border-green-500/20'
              : 'bg-red-500/10 text-red-500 border border-red-500/20'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Trading Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Trading Preferences</CardTitle>
          <CardDescription>
            Default settings for new trades
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="leverage">Default Leverage</Label>
              <select
                id="leverage"
                value={settings.defaultLeverage}
                onChange={(e) =>
                  setSettings({ ...settings, defaultLeverage: Number(e.target.value) })
                }
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
              <Label htmlFor="lotSize">Default Lot Size</Label>
              <Input
                id="lotSize"
                type="number"
                step="0.01"
                value={settings.defaultLotSize}
                onChange={(e) =>
                  setSettings({ ...settings, defaultLotSize: Number(e.target.value) })
                }
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="riskPerTrade">Risk Per Trade (%)</Label>
            <Input
              id="riskPerTrade"
              type="number"
              step="0.5"
              value={settings.riskPerTrade}
              onChange={(e) =>
                setSettings({ ...settings, riskPerTrade: Number(e.target.value) })
              }
              className="max-w-xs"
            />
            <p className="text-xs text-muted-foreground">
              Maximum percentage of account to risk per trade
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Display Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Display Settings</CardTitle>
          <CardDescription>
            Customize your interface
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="currency">Display Currency</Label>
              <select
                id="currency"
                value={settings.currency}
                onChange={(e) =>
                  setSettings({ ...settings, currency: e.target.value })
                }
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="JPY">JPY</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <select
                id="timezone"
                value={settings.timezone}
                onChange={(e) =>
                  setSettings({ ...settings, timezone: e.target.value })
                }
                className="w-full h-10 px-3 rounded-md border border-input bg-background"
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time (ET)</option>
                <option value="America/Chicago">Central Time (CT)</option>
                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                <option value="Europe/London">London (GMT)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="theme">Theme</Label>
            <select
              id="theme"
              value={settings.theme}
              onChange={(e) =>
                setSettings({ ...settings, theme: e.target.value })
              }
              className="w-full h-10 px-3 rounded-md border border-input bg-background max-w-xs"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>
            Configure how you receive alerts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Notifications</p>
              <p className="text-sm text-muted-foreground">
                Receive daily summary emails
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.emailNotifications}
                onChange={(e) =>
                  setSettings({ ...settings, emailNotifications: e.target.checked })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-muted rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Trade Alerts</p>
              <p className="text-sm text-muted-foreground">
                Get notified when orders are filled
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.tradeAlerts}
                onChange={(e) =>
                  setSettings({ ...settings, tradeAlerts: e.target.checked })
                }
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-muted rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Account */}
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>
            Manage your account settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground">Signed in as</p>
            <p className="font-medium">{profile?.email || 'Demo Account'}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {profile?.name || 'Demo Trader'}
            </p>
          </div>

          <Separator />

          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full"
              onClick={handleReset}
              disabled={resetting}
            >
              {resetting ? 'Resetting...' : 'Reset Paper Trading Account'}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              This will reset your balance to $100,000 and clear all trade history
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </div>
  );
}
