'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';

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

  const handleSave = () => {
    console.log('Saving settings:', settings);
    // TODO: Save to backend
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your trading preferences and account settings
        </p>
      </div>

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
            <p className="font-medium">user@example.com</p>
            <p className="text-xs text-muted-foreground mt-1">
              Google Account
            </p>
          </div>

          <Separator />

          <div className="space-y-2">
            <Button variant="outline" className="w-full">
              Reset Paper Trading Account
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              This will reset your balance to $100,000 and clear all trade history
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave}>Save Changes</Button>
      </div>
    </div>
  );
}
