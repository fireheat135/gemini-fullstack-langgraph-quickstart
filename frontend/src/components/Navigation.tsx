import { useState } from 'react';
import { cn } from '@/lib/utils';

type ActiveView = 'research' | 'seo' | 'content' | 'api-keys';

interface NavigationProps {
  activeView: ActiveView;
  onViewChange: (view: ActiveView) => void;
}

export function Navigation({ activeView, onViewChange }: NavigationProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems = [
    {
      id: 'research' as ActiveView,
      label: 'リサーチ',
      icon: '🔍',
      description: 'AI研究エージェント'
    },
    {
      id: 'seo' as ActiveView,
      label: 'SEO分析',
      icon: '📊',
      description: 'SEO最適化ダッシュボード'
    },
    {
      id: 'content' as ActiveView,
      label: 'コンテンツ',
      icon: '✍️',
      description: 'AI記事生成'
    },
    {
      id: 'api-keys' as ActiveView,
      label: 'API設定',
      icon: '🔑',
      description: 'APIキー管理'
    }
  ];

  return (
    <div 
      className={cn(
        "bg-neutral-900 border-r border-neutral-700 flex flex-col transition-all duration-300",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-neutral-700 flex items-center justify-between">
        {!isCollapsed && (
          <div>
            <h1 className="text-lg font-bold text-white">SEO Agent</h1>
            <p className="text-sm text-neutral-400">AI-Powered Platform</p>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-2 hover:bg-neutral-700 rounded-md transition-colors"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onViewChange(item.id)}
                className={cn(
                  "w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200",
                  "hover:bg-neutral-700",
                  activeView === item.id
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-neutral-300 hover:text-white"
                )}
              >
                <span className="text-xl">{item.icon}</span>
                {!isCollapsed && (
                  <div className="flex-1 text-left">
                    <div className="font-medium">{item.label}</div>
                    <div className="text-xs opacity-75">{item.description}</div>
                  </div>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="p-4 border-t border-neutral-700">
          <div className="text-xs text-neutral-500 text-center">
            <div>v1.0.0</div>
            <div>Powered by LangGraph</div>
          </div>
        </div>
      )}
    </div>
  );
}