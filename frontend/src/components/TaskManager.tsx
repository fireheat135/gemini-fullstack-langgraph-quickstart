import React, { useState, useCallback } from 'react'
import { 
  CheckCircle2, 
  Clock, 
  Plus, 
  Filter, 
  Calendar, 
  Target, 
  Brain,
  Zap,
  AlertCircle,
  MoreHorizontal,
  Star,
  Users,
  ArrowRight
} from 'lucide-react'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'

interface Task {
  id: string
  title: string
  description: string
  status: 'todo' | 'in_progress' | 'review' | 'done'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  type: 'research' | 'writing' | 'review' | 'analysis' | 'planning'
  dueDate: string
  estimatedHours: number
  actualHours?: number
  tags: string[]
  assignee: string
  progress: number
}

interface TaskManagerProps {
  onTaskSelect?: (task: Task) => void
}

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'SEOキーワード分析レポート作成',
    description: '競合他社のキーワード戦略を分析し、機会を特定する',
    status: 'in_progress',
    priority: 'high',
    type: 'research',
    dueDate: '2024-06-08',
    estimatedHours: 4,
    actualHours: 2.5,
    tags: ['SEO', 'キーワード', '競合分析'],
    assignee: 'あなた',
    progress: 65
  },
  {
    id: '2',
    title: 'ブログ記事「AIライティングツール比較」執筆',
    description: '最新のAIライティングツールを比較検討する記事を作成',
    status: 'todo',
    priority: 'medium',
    type: 'writing',
    dueDate: '2024-06-10',
    estimatedHours: 6,
    tags: ['ブログ', 'AI', 'ライティング'],
    assignee: 'あなた',
    progress: 0
  },
  {
    id: '3',
    title: 'コンテンツカレンダー6月分更新',
    description: '6月の投稿スケジュールとテーマを決定',
    status: 'review',
    priority: 'medium',
    type: 'planning',
    dueDate: '2024-06-05',
    estimatedHours: 2,
    actualHours: 1.5,
    tags: ['計画', 'カレンダー'],
    assignee: 'チーム',
    progress: 90
  }
]

export function TaskManager({ onTaskSelect }: TaskManagerProps) {
  const [tasks, setTasks] = useState<Task[]>(mockTasks)
  const [selectedView, setSelectedView] = useState('kanban')
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [showNewTaskForm, setShowNewTaskForm] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo': return 'bg-gray-500/20 text-gray-300'
      case 'in_progress': return 'bg-blue-500/20 text-blue-300'
      case 'review': return 'bg-yellow-500/20 text-yellow-300'
      case 'done': return 'bg-green-500/20 text-green-300'
      default: return 'bg-gray-500/20 text-gray-300'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return 'text-green-400'
      case 'medium': return 'text-yellow-400'
      case 'high': return 'text-orange-400'
      case 'urgent': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'research': return <Target className="h-4 w-4" />
      case 'writing': return <Zap className="h-4 w-4" />
      case 'review': return <CheckCircle2 className="h-4 w-4" />
      case 'analysis': return <Brain className="h-4 w-4" />
      case 'planning': return <Calendar className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getDaysUntilDue = (dueDate: string) => {
    const due = new Date(dueDate)
    const today = new Date()
    const diffTime = due.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const isOverdue = (dueDate: string) => {
    return getDaysUntilDue(dueDate) < 0
  }

  const handleCreateTask = useCallback(() => {
    if (!newTaskTitle.trim()) return
    
    const newTask: Task = {
      id: Date.now().toString(),
      title: newTaskTitle,
      description: '',
      status: 'todo',
      priority: 'medium',
      type: 'writing',
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      estimatedHours: 2,
      tags: [],
      assignee: 'あなた',
      progress: 0
    }
    
    setTasks([...tasks, newTask])
    setNewTaskTitle('')
    setShowNewTaskForm(false)
  }, [newTaskTitle, tasks])

  const tasksByStatus = {
    todo: tasks.filter(task => task.status === 'todo'),
    in_progress: tasks.filter(task => task.status === 'in_progress'),
    review: tasks.filter(task => task.status === 'review'),
    done: tasks.filter(task => task.status === 'done')
  }

  const KanbanColumn = ({ title, status, tasks: columnTasks, color }: { 
    title: string
    status: string
    tasks: Task[]
    color: string 
  }) => (
    <div className="flex-1 min-w-72">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${color}`} />
            {title}
            <Badge variant="outline" className="ml-1">
              {columnTasks.length}
            </Badge>
          </h3>
        </div>
      </div>
      
      <div className="space-y-3">
        {columnTasks.map((task) => (
          <Card 
            key={task.id}
            className="p-4 cursor-pointer glass-effect hover:shadow-lg transition-all duration-200 hover:bg-accent/5"
            onClick={() => onTaskSelect?.(task)}
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-foreground line-clamp-2">
                    {task.title}
                  </h4>
                  {task.description && (
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {task.description}
                    </p>
                  )}
                </div>
                <Button variant="ghost" size="icon" className="h-6 w-6 ml-2">
                  <MoreHorizontal className="h-3 w-3" />
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <div className={`p-1 rounded ${getStatusColor(task.status)}`}>
                  {getTypeIcon(task.type)}
                </div>
                <Badge 
                  variant="outline" 
                  className={`text-xs ${getPriorityColor(task.priority)} border-current`}
                >
                  {task.priority}
                </Badge>
              </div>

              {task.progress > 0 && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">進捗</span>
                    <span className="text-primary">{task.progress}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-1.5">
                    <div 
                      className="bg-primary h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Calendar className="h-3 w-3" />
                  <span className={`${isOverdue(task.dueDate) ? 'text-red-400' : 'text-muted-foreground'}`}>
                    {isOverdue(task.dueDate) && <AlertCircle className="h-3 w-3 inline mr-1" />}
                    {task.dueDate}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  <span className="text-muted-foreground">
                    {task.actualHours || 0}h / {task.estimatedHours}h
                  </span>
                </div>
              </div>

              {task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {task.tags.slice(0, 3).map((tag, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {task.tags.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{task.tags.length - 3}
                    </Badge>
                  )}
                </div>
              )}
            </div>
          </Card>
        ))}
        
        {status === 'todo' && (
          <Card className="p-4 border-dashed border-border/50 hover:border-primary/50 transition-colors">
            {showNewTaskForm ? (
              <div className="space-y-3">
                <Input
                  placeholder="タスク名を入力..."
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="bg-background/50"
                  onKeyPress={(e) => e.key === 'Enter' && handleCreateTask()}
                  autoFocus
                />
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleCreateTask}>
                    作成
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    onClick={() => setShowNewTaskForm(false)}
                  >
                    キャンセル
                  </Button>
                </div>
              </div>
            ) : (
              <Button
                variant="ghost"
                className="w-full justify-start text-muted-foreground hover:text-foreground"
                onClick={() => setShowNewTaskForm(true)}
              >
                <Plus className="h-4 w-4 mr-2" />
                新しいタスクを追加
              </Button>
            )}
          </Card>
        )}
      </div>
    </div>
  )

  return (
    <div className="h-full flex flex-col space-y-6 p-6 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <CheckCircle2 className="h-6 w-6 text-primary" />
          タスク管理
          <Badge className="ml-2 bg-primary/20 text-primary border-primary/50">
            Smart Workflow
          </Badge>
        </h1>
        <p className="text-muted-foreground">
          AIが最適化するタスク管理で、生産性を最大化します
        </p>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4" />
            フィルター
          </Button>
          <Button variant="outline" size="sm">
            <Users className="h-4 w-4" />
            担当者
          </Button>
          <Button variant="glow" size="sm">
            <Brain className="h-4 w-4" />
            AI提案
          </Button>
        </div>
        
        <div className="flex gap-2">
          <Button
            variant={selectedView === 'kanban' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedView('kanban')}
          >
            かんばん
          </Button>
          <Button
            variant={selectedView === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedView('list')}
          >
            リスト
          </Button>
          <Button
            variant={selectedView === 'calendar' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedView('calendar')}
          >
            カレンダー
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {selectedView === 'kanban' && (
          <div className="h-full overflow-x-auto">
            <div className="flex gap-6 h-full pb-6">
              <KanbanColumn
                title="To Do"
                status="todo"
                tasks={tasksByStatus.todo}
                color="bg-gray-500"
              />
              <KanbanColumn
                title="進行中"
                status="in_progress"
                tasks={tasksByStatus.in_progress}
                color="bg-blue-500"
              />
              <KanbanColumn
                title="レビュー"
                status="review"
                tasks={tasksByStatus.review}
                color="bg-yellow-500"
              />
              <KanbanColumn
                title="完了"
                status="done"
                tasks={tasksByStatus.done}
                color="bg-green-500"
              />
            </div>
          </div>
        )}

        {selectedView === 'list' && (
          <Card className="h-full glass-effect p-6">
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <CheckCircle2 className="h-12 w-12 mx-auto text-muted-foreground" />
                <h3 className="text-lg font-semibold">リストビュー</h3>
                <p className="text-muted-foreground">
                  タスクのリスト表示を準備中...
                </p>
              </div>
            </div>
          </Card>
        )}

        {selectedView === 'calendar' && (
          <Card className="h-full glass-effect p-6">
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <Calendar className="h-12 w-12 mx-auto text-muted-foreground" />
                <h3 className="text-lg font-semibold">カレンダービュー</h3>
                <p className="text-muted-foreground">
                  タスクのスケジュール表示を準備中...
                </p>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}