import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { LoginForm } from './LoginForm'
import { RegisterForm } from './RegisterForm'

interface AuthDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultMode?: 'login' | 'register'
}

export function AuthDialog({ open, onOpenChange, defaultMode = 'login' }: AuthDialogProps) {
  const [mode, setMode] = useState<'login' | 'register'>(defaultMode)

  const handleSuccess = () => {
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="sr-only">
          <DialogTitle>
            {mode === 'login' ? 'ログイン' : '新規登録'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'login' 
              ? 'アカウントにサインインしてください' 
              : '新しいアカウントを作成してください'
            }
          </DialogDescription>
        </DialogHeader>
        {mode === 'login' ? (
          <LoginForm 
            onSuccess={handleSuccess}
            onRegisterClick={() => setMode('register')}
          />
        ) : (
          <RegisterForm 
            onSuccess={handleSuccess}
            onLoginClick={() => setMode('login')}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}