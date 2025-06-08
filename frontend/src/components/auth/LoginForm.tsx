import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { Loader2, LogIn } from 'lucide-react'
import { useAuth } from './AuthContext'
import apiClient from '@/lib/api'

const loginSchema = z.object({
  email: z.string().email('有効なメールアドレスを入力してください'),
  password: z.string().min(6, 'パスワードは6文字以上で入力してください'),
})

type LoginFormData = z.infer<typeof loginSchema>

interface LoginFormProps {
  onSuccess?: () => void
  onRegisterClick?: () => void
}

export function LoginForm({ onSuccess, onRegisterClick }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const { login } = useAuth()

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true)
    try {
      await login(data.email, data.password)
      onSuccess?.()
    } catch (error) {
      form.setError('root', {
        message: error instanceof Error ? error.message : 'ログインに失敗しました',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true)
    try {
      const response = await apiClient.getGoogleAuthUrl()
      // Redirect to Google OAuth2
      window.location.href = response.data.auth_url
    } catch (error) {
      form.setError('root', {
        message: error instanceof Error ? error.message : 'Googleログインに失敗しました',
      })
    } finally {
      setIsGoogleLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">
          ログイン
        </CardTitle>
        <CardDescription className="text-center">
          アカウントにサインインしてください
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>メールアドレス</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      type="email"
                      placeholder="example@example.com"
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>パスワード</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      type="password"
                      placeholder="••••••••"
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {form.formState.errors.root && (
              <div className="text-sm font-medium text-destructive">
                {form.formState.errors.root.message}
              </div>
            )}
            <Button type="submit" className="w-full" disabled={isLoading || isGoogleLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ログイン中...
                </>
              ) : (
                <>
                  <LogIn className="mr-2 h-4 w-4" />
                  ログイン
                </>
              )}
            </Button>
          </form>
        </Form>
        
        <div className="mt-4">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">または</span>
            </div>
          </div>
          <Button
            type="button"
            variant="outline"
            className="w-full mt-4"
            onClick={handleGoogleLogin}
            disabled={isLoading || isGoogleLoading}
          >
            {isGoogleLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Google認証中...
              </>
            ) : (
              <>
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Googleでログイン
              </>
            )}
          </Button>
        </div>
        <div className="mt-4 text-center text-sm">
          アカウントをお持ちでない方は{' '}
          <button
            type="button"
            onClick={onRegisterClick}
            className="font-medium text-primary underline underline-offset-4 hover:text-primary/80"
          >
            新規登録
          </button>
        </div>
      </CardContent>
    </Card>
  )
}